"""冒烟测试：不起 HTTP，直接验证能动 Agent 的闭环。

跑若干轮感知，观察是否产生解读，并手动下发一次"看到我"与投食，确认执行器闭环。
用法： uv run python scripts/smoke.py
"""

from __future__ import annotations

import asyncio
import logging

from anyfamily.agent import Agent
from anyfamily.app import default_profile

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


async def main() -> None:
    agent = Agent(profile=default_profile())
    print("== 设备 ==")
    for d in agent.actuators.devices():
        print(" ", d.name, [c.value for c in d.capabilities])

    print("\n== 跑 10 轮感知（可能触发自主解读/规划/执行） ==")
    for _ in range(10):
        await agent.perceive_once()

    print("\n== 手动：看到我（主人声音安抚） ==")
    await agent.decision.dispatch_manual("speak", {"text": "Lucky 乖，马上回家", "voice": "owner"})

    print("\n== 手动：投食 ==")
    await agent.decision.dispatch_manual("feed", {"portion": "small"})

    print("\n== 今日概览 ==")
    ov = agent.memory.today_overview(agent.profile.id)
    print(" summary:", ov["summary"])
    print(" activities:", ov["activities"])
    print(" actions:", ov["actions"])

    print("\n== 近期解读 ==")
    for i in agent.memory.recent_interpretations(agent.profile.id, limit=5):
        print(f"  [{i.confidence:.2f}] {i.label}  证据={i.evidence}")


if __name__ == "__main__":
    asyncio.run(main())
