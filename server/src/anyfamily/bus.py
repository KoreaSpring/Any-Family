"""异步事件总线（观察者模式）。

各层订阅感兴趣的事件类型，发布者无需知道谁在消费，彼此解耦。
MVP 用进程内 asyncio 实现；后续若多进程/多机，可换成 MQTT 等而不动上层代码。
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable

from .events import Event, EventType

logger = logging.getLogger("anyfamily.bus")

Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[EventType, list[Handler]] = defaultdict(list)
        self._any: list[Handler] = []  # 订阅所有事件（如记忆层、日志）

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._subs[event_type].append(handler)

    def subscribe_all(self, handler: Handler) -> None:
        self._any.append(handler)

    async def publish(self, event: Event) -> None:
        """并发分发给所有匹配的订阅者；单个 handler 异常不影响其他。"""
        handlers = [*self._subs.get(event.type, []), *self._any]
        if not handlers:
            return
        results = await asyncio.gather(
            *(self._safe(h, event) for h in handlers), return_exceptions=True
        )
        for r in results:
            if isinstance(r, Exception):
                logger.exception("事件处理器异常: %s", r)

    @staticmethod
    async def _safe(handler: Handler, event: Event) -> None:
        await handler(event)
