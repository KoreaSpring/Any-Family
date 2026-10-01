"""Agent 门面：把感知/记忆/规划/执行器各层接到同一条事件总线上。

对外提供一个干净的入口，供 app 启动与 api 调用。
"""

from __future__ import annotations

import logging

from .bus import EventBus
from .devices import ActuatorRegistry, Device, MockCompanionDevice
from .llm import LLMProvider, build_provider
from .memory import MemoryStore
from .perception import Detector, PerceptionLoop, StubDetector
from .planning import DecisionEngine
from .models import PetProfile

logger = logging.getLogger("anyfamily.agent")


class Agent:
    def __init__(
        self,
        profile: PetProfile,
        detector: Detector | None = None,
        devices: list[Device] | None = None,
        llm: LLMProvider | None = None,
    ) -> None:
        self.profile = profile
        self.bus = EventBus()
        self.memory = MemoryStore()
        self.actuators = ActuatorRegistry(self.bus)
        self.llm = llm or build_provider()

        # 记忆层订阅所有事件做落地
        self.bus.subscribe_all(self.memory.on_event)

        # 注册设备（默认模拟硬件，接真实硬件时传入适配器）
        for d in devices or [MockCompanionDevice()]:
            self.actuators.register(d)

        # 决策闭环（注入 LLM，不可用自动回退规则版）
        self.decision = DecisionEngine(self.bus, self.memory, self.actuators, profile, self.llm)

        # 感知循环
        self.perception = PerceptionLoop(self.bus, detector or StubDetector())

    async def perceive_once(self) -> list:
        """驱动一次感知 → 自动触发解读/规划/执行闭环。"""
        return await self.perception.tick(self.profile.id)

    def update_profile(self, patch: dict) -> PetProfile:
        """引导录入/完善资料：局部更新宠物档案。

        决策引擎持有同一个 profile 引用，就地更新即可生效。
        """
        data = self.profile.model_dump()
        for k, v in patch.items():
            if k in data and v is not None:
                data[k] = v
        updated = PetProfile(**data)
        # 保留 id，并把字段同步回原对象（决策引擎引用不变）
        for field_name, value in updated.model_dump().items():
            setattr(self.profile, field_name, value)
        return self.profile
