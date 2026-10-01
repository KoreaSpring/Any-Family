"""Agent 门面：把感知/记忆/规划/执行器各层接到同一条事件总线上。

对外提供一个干净的入口，供 app 启动与 api 调用。
"""

from __future__ import annotations

import logging

from .bus import EventBus
from .devices import ActuatorRegistry, Device, MockCompanionDevice
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
    ) -> None:
        self.profile = profile
        self.bus = EventBus()
        self.memory = MemoryStore()
        self.actuators = ActuatorRegistry(self.bus)

        # 记忆层订阅所有事件做落地
        self.bus.subscribe_all(self.memory.on_event)

        # 注册设备（默认模拟硬件，接真实硬件时传入适配器）
        for d in devices or [MockCompanionDevice()]:
            self.actuators.register(d)

        # 决策闭环
        self.decision = DecisionEngine(self.bus, self.memory, self.actuators, profile)

        # 感知循环
        self.perception = PerceptionLoop(self.bus, detector or StubDetector())

    async def perceive_once(self) -> list:
        """驱动一次感知 → 自动触发解读/规划/执行闭环。"""
        return await self.perception.tick(self.profile.id)
