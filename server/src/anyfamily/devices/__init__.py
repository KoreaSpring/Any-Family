"""设备层：把宠物陪伴硬件抽象成 Agent 可调用的能力工具。

接入新硬件（EPPO / 投食器 / 摄像头等）只需实现 Device 接口，
上层 Agent 的规划与执行逻辑无需改动。
"""

from .base import Capability, Device, DeviceInfo
from .mock import MockCompanionDevice
from .registry import ActuatorRegistry

__all__ = [
    "Capability",
    "Device",
    "DeviceInfo",
    "MockCompanionDevice",
    "ActuatorRegistry",
]
