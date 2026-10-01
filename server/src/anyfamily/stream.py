"""实时事件推送（SSE）。

订阅事件总线上的所有事件，广播给所有连接的浏览器，让 Web 控制台能实时看到
感知 → 解读 → 规划 → 执行的事件滴落。
"""

from __future__ import annotations

import asyncio
import logging

from .bus import EventBus
from .events import Event

logger = logging.getLogger("anyfamily.stream")


class EventBroadcaster:
    """把总线事件扇出给多个 SSE 订阅者（每个浏览器连接一个队列）。"""

    def __init__(self, bus: EventBus, max_queue: int = 100) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()
        self._max_queue = max_queue
        bus.subscribe_all(self._on_event)

    async def _on_event(self, event: Event) -> None:
        data = event.model_dump_json()
        for q in list(self._subscribers):
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                # 慢消费者丢最旧的，保证实时性
                try:
                    q.get_nowait()
                    q.put_nowait(data)
                except asyncio.QueueEmpty:
                    pass

    def register(self) -> asyncio.Queue[str]:
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=self._max_queue)
        self._subscribers.add(q)
        return q

    def unregister(self, q: asyncio.Queue[str]) -> None:
        self._subscribers.discard(q)

    async def sse(self, q: asyncio.Queue[str]):
        """生成 SSE 数据流。"""
        try:
            # 连接即发一个 hello，证明通道活着
            yield "event: hello\ndata: {}\n\n"
            while True:
                data = await q.get()
                yield f"data: {data}\n\n"
        finally:
            self.unregister(q)
