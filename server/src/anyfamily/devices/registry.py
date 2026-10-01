"""执行器注册表：Agent 决策 → 硬件执行的桥。

订阅 action.request 事件，路由到支持该能力的设备执行，回发 action.result。
这样决策层只管"想做什么"（能力 + 参数），不关心具体哪台硬件、怎么下指令。
"""

from __future__ import annotations

import logging

from ..bus import EventBus
from ..events import Event, EventType, action_result
from .base import Capability, Device, DeviceInfo

logger = logging.getLogger("anyfamily.devices.registry")


class ActuatorRegistry:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self._devices: list[Device] = []
        bus.subscribe(EventType.ACTION_REQUEST, self._on_action_request)

    def register(self, device: Device) -> None:
        self._devices.append(device)
        logger.info(
            "注册设备 %s (%s) 能力: %s",
            device.name,
            device.device_id,
            [c.value for c in device.capabilities],
        )

    def devices(self) -> list[DeviceInfo]:
        return [d.info() for d in self._devices]

    def available_capabilities(self) -> list[Capability]:
        caps: set[Capability] = set()
        for d in self._devices:
            if d.online:
                caps.update(d.capabilities)
        return sorted(caps, key=lambda c: c.value)

    def _find(self, capability: Capability) -> Device | None:
        for d in self._devices:
            if d.online and d.supports(capability):
                return d
        return None

    async def _on_action_request(self, event: Event) -> None:
        cap_raw = event.payload.get("capability")
        args = event.payload.get("args", {})
        try:
            capability = Capability(cap_raw)
        except ValueError:
            logger.warning("未知能力: %s", cap_raw)
            await self.bus.publish(
                action_result(
                    event.pet_id or "", str(cap_raw), ok=False,
                    source="actuator", detail="未知能力",
                )
            )
            return

        device = self._find(capability)
        if device is None:
            logger.warning("没有在线设备支持能力: %s", capability.value)
            await self.bus.publish(
                action_result(
                    event.pet_id or "", capability.value, ok=False,
                    source="actuator", detail="无可用设备",
                )
            )
            return

        result = await device.execute(capability, args)
        await self.bus.publish(
            action_result(
                event.pet_id or "",
                capability.value,
                ok=result.ok,
                source=f"actuator:{device.device_id}",
                detail=result.detail,
                **result.data,
            )
        )
