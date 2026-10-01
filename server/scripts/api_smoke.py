"""接口冒烟：用 FastAPI TestClient 在进程内验证所有 REST 接口。

避免受 shell 引号/转义影响。用法： uv run python scripts/api_smoke.py
需要 dev 依赖 httpx（TestClient 依赖）。
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from anyfamily.agent import Agent
from anyfamily.api import create_app
from anyfamily.app import default_profile


def main() -> None:
    agent = Agent(profile=default_profile())
    client = TestClient(create_app(agent))

    def check(name: str, resp) -> None:
        ok = resp.status_code == 200
        print(f"[{'OK ' if ok else 'ERR'}] {name} -> {resp.status_code}")
        assert ok, resp.text

    check("GET /health", client.get("/health"))
    check("GET /pet", client.get("/pet"))
    check("GET /devices", client.get("/devices"))

    # 先驱动几轮感知，产生时间线与解读
    for _ in range(8):
        client.post("/perceive-once")

    check("GET /overview", (ov := client.get("/overview")))
    print("     summary:", ov.json()["summary"])

    check("GET /timeline", client.get("/timeline"))
    check("GET /interpretations", client.get("/interpretations"))

    # 三个手动指令
    check("POST /speak", client.post("/speak", json={"text": "Lucky 乖", "voice": "owner"}))
    check("POST /play", client.post("/play", json={"mode": "laser", "duration_s": 20}))
    check("POST /feed", client.post("/feed", json={"portion": "small"}))

    print("\n全部接口通过。")


if __name__ == "__main__":
    main()
