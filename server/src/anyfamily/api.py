"""FastAPI 接口：供父母端 App 调用。

闭环已在 Agent 内部打通，这里只暴露查询与手动指令。
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agent import Agent
from .models import PetProfile


class SpeakRequest(BaseModel):
    text: str
    voice: str = "owner"  # owner=主人声音库, tts=合成


class PlayRequest(BaseModel):
    mode: str = "laser"
    duration_s: int = 30


class FeedRequest(BaseModel):
    portion: str = "small"


def create_app(agent: Agent) -> FastAPI:
    app = FastAPI(title="Any-Family Server", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/pet")
    async def get_pet() -> PetProfile:
        return agent.profile

    @app.get("/devices")
    async def devices() -> list[dict[str, Any]]:
        return [d.model_dump() for d in agent.actuators.devices()]

    @app.get("/overview")
    async def overview() -> dict[str, Any]:
        return agent.memory.today_overview(agent.profile.id)

    @app.get("/timeline")
    async def timeline(day: str | None = None, limit: int = 200) -> list[dict]:
        return agent.memory.read_timeline(day=day, limit=limit)

    @app.get("/interpretations")
    async def interpretations(limit: int = 20) -> list[dict]:
        return [i.model_dump() for i in agent.memory.recent_interpretations(agent.profile.id, limit)]

    @app.get("/health-alerts")
    async def health_alerts() -> list[dict]:
        return [h.model_dump() for h in agent.memory.health_alerts(agent.profile.id)]

    # ---- 手动指令：三个入口里的"看到我"/逗玩/投食 ----
    @app.post("/speak")
    async def speak(req: SpeakRequest) -> dict[str, str]:
        # "看到我"：用熟悉的话 + 主人声音远程播放
        await agent.decision.dispatch_manual("speak", req.model_dump())
        return {"status": "dispatched"}

    @app.post("/play")
    async def play(req: PlayRequest) -> dict[str, str]:
        await agent.decision.dispatch_manual("play", req.model_dump())
        return {"status": "dispatched"}

    @app.post("/feed")
    async def feed(req: FeedRequest) -> dict[str, str]:
        await agent.decision.dispatch_manual("feed", req.model_dump())
        return {"status": "dispatched"}

    # ---- 演示：手动驱动一次感知，走完解读→规划→执行闭环 ----
    @app.post("/perceive-once")
    async def perceive_once() -> dict[str, Any]:
        events = await agent.perceive_once()
        return {"emitted": [e.model_dump() for e in events]}

    return app
