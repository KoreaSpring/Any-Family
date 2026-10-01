"""验证 LLM 层：无 Key 时应回退规则版，Agent 与 /ask 仍正常。

用法： uv run python scripts/llm_check.py
"""

from __future__ import annotations

import asyncio

from anyfamily.agent import Agent
from anyfamily.app import default_profile


async def main() -> None:
    agent = Agent(profile=default_profile())
    print("LLM backend:", agent.llm.name, "available:", agent.llm.available)
    assert agent.llm.name == "none", "默认应为回退(none)"

    # 跑几轮感知产生素材
    for _ in range(6):
        await agent.perceive_once()

    res = await agent.decision.answer("它今天怎么样？")
    print("llm:", res["llm"])
    print("answer:", res["answer"])
    print("evidence:", res["evidence"][:3])
    assert res["llm"] is False, "无 Key 应走回退"
    assert res["answer"], "回答不应为空"
    print("\nLLM 层验证通过（无 Key 正确回退，Agent/ask 正常）。")


if __name__ == "__main__":
    asyncio.run(main())
