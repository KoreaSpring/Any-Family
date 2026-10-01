"""模拟陪伴硬件：实现全部四种能力，用于在无真实硬件时跑通闭环。

它模拟你已有的那台硬件：双向语音 / 摄像头 / 逗玩 / 投食。
接真实硬件时，照着这个类实现一个真实适配器即可（发 BLE/REST/MQTT 指令）。
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from ..config import settings
from .base import ActionResult, Capability, Device

logger = logging.getLogger("anyfamily.devices.mock")


class MockCompanionDevice(Device):
    def __init__(self, device_id: str = "mock-eppo-01", name: str = "客厅陪伴机器人") -> None:
        super().__init__(device_id=device_id, name=name, model="MockCompanion")
        # 投食安全：限制每日投食次数，避免 agent 失控狂投
        self.feed_count_today = 0
        self.max_feeds_per_day = 6

    @property
    def capabilities(self) -> list[Capability]:
        return [Capability.SPEAK, Capability.CAMERA, Capability.PLAY, Capability.FEED]

    async def execute(self, capability: Capability, args: dict[str, Any]) -> ActionResult:
        handler = {
            Capability.SPEAK: self._speak,
            Capability.CAMERA: self._camera,
            Capability.PLAY: self._play,
            Capability.FEED: self._feed,
        }[capability]
        return await handler(args)

    async def _speak(self, args: dict[str, Any]) -> ActionResult:
        text = args.get("text", "")
        voice = args.get("voice", "owner")  # owner=主人声音库, tts=合成
        logger.info("[SPEAK] (%s) 播放: %s", voice, text)
        return ActionResult(ok=True, capability=Capability.SPEAK, detail=f"已播放: {text}")

    async def _camera(self, args: dict[str, Any]) -> ActionResult:
        # 模拟抓一帧，写占位文件到 media 目录
        settings.ensure_dirs()
        fname = f"snapshot_{int(time.time())}.jpg"
        fpath: Path = settings.data_dir / "media" / fname
        fpath.write_bytes(b"\xff\xd8\xff\xe0MOCK_SNAPSHOT")  # 假 JPEG 头 + 占位
        logger.info("[CAMERA] 抓帧 -> %s", fname)
        return ActionResult(
            ok=True, capability=Capability.CAMERA, detail="已抓帧", data={"media": f"media/{fname}"}
        )

    async def _play(self, args: dict[str, Any]) -> ActionResult:
        mode = args.get("mode", "laser")  # laser/toss_toy/move
        duration = int(args.get("duration_s", 30))
        logger.info("[PLAY] 逗玩 mode=%s %ss", mode, duration)
        return ActionResult(
            ok=True, capability=Capability.PLAY, detail=f"逗玩 {mode} {duration}s"
        )

    async def _feed(self, args: dict[str, Any]) -> ActionResult:
        portion = args.get("portion", "small")
        if self.feed_count_today >= self.max_feeds_per_day:
            logger.warning("[FEED] 已达每日投食上限，拒绝")
            return ActionResult(
                ok=False, capability=Capability.FEED, detail="已达每日投食上限，拒绝执行"
            )
        self.feed_count_today += 1
        logger.info("[FEED] 投食 portion=%s (今日第 %d 次)", portion, self.feed_count_today)
        return ActionResult(
            ok=True,
            capability=Capability.FEED,
            detail=f"已投食 {portion}",
            data={"feed_count_today": self.feed_count_today},
        )
