"""设备接口与能力定义。

接入真实硬件时，继承 Device、声明 capabilities、实现 execute() 即可。
业界范式（RoboNeuron / ROS-LLM）：把硬件能力暴露成 agent 可调用的工具，
严格解耦"大脑(规划)"与"小脑(控制)"。这里 Device 就是"小脑"的统一外壳。
"""

from __future__ import annotations

import abc
from enum import Enum
from typing import Any

from pydantic import BaseModel


class Capability(str, Enum):
    """硬件能提供的能力（= Agent 可调用的工具）。"""

    SPEAK = "speak"      # 远程语音：用熟悉的话/主人声音安抚或下指令
    CAMERA = "camera"    # 看：抓一帧/取一段，用于感知与父母直播
    PLAY = "play"        # 逗宠物：移动/逗玩/激光/发声玩具等
    FEED = "feed"        # 投食：投放零食/粮

    @property
    def description(self) -> str:
        return {
            Capability.SPEAK: "用熟悉的指令词或主人声音远程播放",
            Capability.CAMERA: "抓取当前画面帧或一段短视频",
            Capability.PLAY: "驱动硬件逗宠物（移动/发声/激光等）",
            Capability.FEED: "投放零食或口粮",
        }[self]


class DeviceInfo(BaseModel):
    device_id: str
    name: str
    model: str
    capabilities: list[Capability]
    online: bool = True


class ActionResult(BaseModel):
    ok: bool
    capability: Capability
    detail: str = ""
    data: dict[str, Any] = {}  # 如 camera 返回媒体路径


class Device(abc.ABC):
    """硬件设备统一接口。真实硬件适配器继承它。"""

    def __init__(self, device_id: str, name: str, model: str) -> None:
        self.device_id = device_id
        self.name = name
        self.model = model
        self.online = True

    @property
    @abc.abstractmethod
    def capabilities(self) -> list[Capability]:
        """本设备支持的能力。"""

    def info(self) -> DeviceInfo:
        return DeviceInfo(
            device_id=self.device_id,
            name=self.name,
            model=self.model,
            capabilities=self.capabilities,
            online=self.online,
        )

    def supports(self, capability: Capability) -> bool:
        return capability in self.capabilities

    @abc.abstractmethod
    async def execute(self, capability: Capability, args: dict[str, Any]) -> ActionResult:
        """执行一个能力动作。真实硬件在此发 BLE/REST/MQTT 指令。"""
