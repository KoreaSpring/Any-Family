"""感知层：从数据源产出结构化 perception.* 事件。

设计为可替换：Detector 是接口，MVP 用 StubDetector（无需真实模型，模拟硬件
摄像头/麦克风看到/听到的东西），真实接入时换成 YOLO 检测 + VLM 语义 + 叫声情绪。
按 RESEARCH.md 第 3 章的级联漏斗，真实实现应：运动门控→检测→事件触发 VLM。
"""

from __future__ import annotations

import abc
import logging
import random

from .bus import EventBus
from .events import Event, activity_event, presence_event, vocal_event
from .models import EmotionVA

logger = logging.getLogger("anyfamily.perception")


class Detector(abc.ABC):
    """感知检测器接口。真实实现：YOLO/VLM/叫声情绪模型。"""

    @abc.abstractmethod
    async def detect(self, pet_id: str) -> list[Event]:
        """对当前一帧/一段，产出若干 perception 事件。"""


class StubDetector(Detector):
    """模拟检测器：随机产出合理的感知事件，用于跑通闭环与演示。

    不依赖任何模型/硬件，保证 `uv run` 直接可跑。
    """

    def __init__(self, source: str = "stub-camera") -> None:
        self.source = source

    async def detect(self, pet_id: str) -> list[Event]:
        events: list[Event] = []
        # 1) 是否在画面
        present = random.random() > 0.2
        events.append(presence_event(pet_id, present=present, source=self.source))
        if not present:
            return events

        # 2) 在干嘛
        activity = random.choices(
            ["sleeping", "eating", "playing", "restless", "idle", "moving"],
            weights=[30, 10, 15, 10, 25, 10],
        )[0]
        events.append(activity_event(pet_id, activity=activity, source=self.source))

        # 3) 偶尔发声（带 VA 情绪）——躁动时更可能叫、唤醒度更高
        if activity == "restless" or random.random() > 0.7:
            arousal = 0.8 if activity == "restless" else random.uniform(0.3, 0.6)
            valence = -0.4 if activity == "restless" else random.uniform(-0.2, 0.4)
            kind = "whine" if valence < 0 else "bark"
            events.append(
                vocal_event(
                    pet_id, kind=kind,
                    emotion=EmotionVA(valence=round(valence, 2), arousal=round(arousal, 2)),
                    source="stub-mic",
                )
            )
        return events


class PerceptionLoop:
    """周期性驱动检测器，把事件发到总线。"""

    def __init__(self, bus: EventBus, detector: Detector) -> None:
        self.bus = bus
        self.detector = detector

    async def tick(self, pet_id: str) -> list[Event]:
        events = await self.detector.detect(pet_id)
        for e in events:
            await self.bus.publish(e)
        return events
