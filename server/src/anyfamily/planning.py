"""规划/决策层：让系统成为"能动 Agent"而非监控器。

闭环： 感知事件 → 解读(Interpreter) → 规划(Planner) → 行动请求(action.request)
        → 执行器执行(devices) → 反馈(action.result) → 记忆

- Interpreter：把硬信号（叫声 VA + 活动 + 历史/画像）融合成一句"软解读"（RESEARCH 第 5 章）。
- Planner：根据解读 + 宠物偏好 + 可用设备能力，决定是否行动、调哪个能力。规则实现，预留 LLM。
- DecisionEngine：串起闭环，并带主动陪伴开关与安全约束。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .bus import EventBus
from .config import settings
from .devices import ActuatorRegistry, Capability
from .events import Event, EventType, action_request
from .memory import MemoryStore
from .models import EmotionVA, Interpretation, PetProfile

logger = logging.getLogger("anyfamily.planning")


# ---------------- 解读 ----------------

class Interpreter:
    """把感知事件融合成对宠物状态/需求的解读。

    MVP 为规则版：结合活动、叫声 VA、当前时间与宠物偏好/作息给出带证据的解读。
    真实版可换成多模态 + LLM，但输出结构(Interpretation)保持不变。
    """

    def interpret(self, event: Event, profile: PetProfile) -> Interpretation | None:
        if event.type == EventType.PET_VOCAL:
            return self._from_vocal(event, profile)
        if event.type == EventType.PET_ACTIVITY:
            return self._from_activity(event, profile)
        return None

    def _from_vocal(self, event: Event, profile: PetProfile) -> Interpretation:
        emo = EmotionVA(**event.payload.get("emotion", {}))
        kind = event.payload.get("kind", "bark")
        evidence = [f"发声类型={kind}", f"情绪 valence={emo.valence} arousal={emo.arousal}"]
        # 高唤醒 + 负效价 → 焦虑/求助；高唤醒 + 正效价 → 兴奋想玩
        if emo.arousal >= 0.7 and emo.valence < 0:
            label, conf = "可能在焦虑或求关注", 0.6
        elif emo.arousal >= 0.6 and emo.valence >= 0:
            label, conf = "情绪高涨，可能想玩", 0.55
        else:
            label, conf = "在表达一般性需求", 0.4
        return Interpretation(
            pet_id=profile.id, state=emo, label=label, confidence=conf,
            evidence=evidence, modalities=["audio"],
        )

    def _from_activity(self, event: Event, profile: PetProfile) -> Interpretation | None:
        activity = event.payload.get("activity")
        if activity == "restless":
            return Interpretation(
                pet_id=profile.id, state=EmotionVA(valence=-0.3, arousal=0.7),
                label="有点躁动不安，可能无聊或焦虑", confidence=0.5,
                evidence=["活动=restless"], modalities=["video"],
            )
        return None


# ---------------- 规划 ----------------

@dataclass
class PlanStep:
    capability: Capability
    args: dict[str, Any]
    reason: str


@dataclass
class Plan:
    goal: str
    steps: list[PlanStep] = field(default_factory=list)


class Planner:
    """根据解读决定行动。规则版，预留 LLM Planner 接口。"""

    def plan(
        self,
        interp: Interpretation,
        profile: PetProfile,
        available: list[Capability],
    ) -> Plan | None:
        # 焦虑/求关注：优先用熟悉声音安抚（有 SPEAK 能力时）
        if "焦虑" in interp.label or "求关注" in interp.label:
            steps: list[PlanStep] = []
            if Capability.SPEAK in available:
                phrase = self._comfort_phrase(profile)
                steps.append(PlanStep(Capability.SPEAK, {"text": phrase, "voice": "owner"},
                                      "用主人熟悉的声音安抚，缓解焦虑"))
            if Capability.CAMERA in available:
                steps.append(PlanStep(Capability.CAMERA, {},
                                      "抓一帧记录状态，供父母查看与留证"))
            if steps:
                return Plan(goal="安抚焦虑的宠物", steps=steps)

        # 想玩/无聊：逗玩（有 PLAY 能力时）
        if "想玩" in interp.label or "无聊" in interp.label:
            if Capability.PLAY in available:
                mode = (profile.preferences.get("toys") or ["laser"])[0]
                return Plan(
                    goal="陪宠物玩一会",
                    steps=[PlanStep(Capability.PLAY, {"mode": mode, "duration_s": 30},
                                    "宠物想玩，启动逗玩缓解无聊")],
                )
        return None

    @staticmethod
    def _comfort_phrase(profile: PetProfile) -> str:
        name = profile.name or "宝贝"
        return f"{name}乖，爸爸妈妈一会就回来，别怕。"


# ---------------- 闭环引擎 ----------------

class DecisionEngine:
    def __init__(
        self,
        bus: EventBus,
        memory: MemoryStore,
        actuators: ActuatorRegistry,
        profile: PetProfile,
    ) -> None:
        self.bus = bus
        self.memory = memory
        self.actuators = actuators
        self.profile = profile
        self.interpreter = Interpreter()
        self.planner = Planner()
        bus.subscribe(EventType.PET_VOCAL, self._on_perception)
        bus.subscribe(EventType.PET_ACTIVITY, self._on_perception)

    async def _on_perception(self, event: Event) -> None:
        interp = self.interpreter.interpret(event, self.profile)
        if interp is None:
            return
        self.memory.add_interpretation(interp)
        logger.info("解读: %s (置信度 %.2f)", interp.label, interp.confidence)

        if not settings.proactive_enabled:
            return  # 主动陪伴关闭时，只解读不行动

        available = self.actuators.available_capabilities()
        plan = self.planner.plan(interp, self.profile, available)
        if plan is None:
            return
        logger.info("计划: %s（%d 步）", plan.goal, len(plan.steps))
        for step in plan.steps:
            await self.bus.publish(
                action_request(self.profile.id, step.capability.value, step.args, source="planner")
            )

    async def dispatch_manual(self, capability: str, args: dict[str, Any]) -> None:
        """父母手动下发指令（看到我/逗玩/投食），走同一条执行通道。"""
        await self.bus.publish(
            action_request(self.profile.id, capability, args, source="parent")
        )
