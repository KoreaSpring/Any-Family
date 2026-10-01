"""FastAPI 接口：供父母端 App 调用。

闭环已在 Agent 内部打通，这里只暴露查询与手动指令。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .agent import Agent
from .models import PetProfile
from .stream import EventBroadcaster


class SpeakRequest(BaseModel):
    text: str
    voice: str = "owner"  # owner=主人声音库, tts=合成


class PlayRequest(BaseModel):
    mode: str = "laser"
    duration_s: int = 30


class FeedRequest(BaseModel):
    portion: str = "small"


class AskRequest(BaseModel):
    question: str = "它今天怎么样？"


class ProfilePatch(BaseModel):
    """引导录入/完善资料：全部可选，只更新提供的字段。"""

    name: str | None = None
    breed: str | None = None
    age: float | None = None
    sex: str | None = None
    neutered: bool | None = None
    weight_kg: float | None = None
    habits: dict[str, Any] | None = None
    preferences: dict[str, Any] | None = None
    trained_commands: list[str] | None = None


def create_app(agent: Agent) -> FastAPI:
    app = FastAPI(title="Any-Family Server", version="0.1.0")
    broadcaster = EventBroadcaster(agent.bus)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/pet")
    async def get_pet() -> PetProfile:
        return agent.profile

    @app.post("/pet")
    async def update_pet(patch: ProfilePatch) -> PetProfile:
        return agent.update_profile(patch.model_dump(exclude_none=True))

    @app.get("/llm-status")
    async def llm_status() -> dict[str, Any]:
        return {"backend": agent.llm.name, "available": agent.llm.available}

    @app.post("/ask")
    async def ask(req: AskRequest) -> dict[str, Any]:
        return await agent.decision.answer(req.question)

    @app.get("/events")
    async def events() -> StreamingResponse:
        q = broadcaster.register()
        return StreamingResponse(
            broadcaster.sse(q),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

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

    # ---- Web 控制台静态页（挂在最后，不遮挡上面的 API 路由）----
    web_dir = Path(__file__).resolve().parent.parent.parent / "web"
    if web_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="web")

    return app
