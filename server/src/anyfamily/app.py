"""应用入口：组装 Agent + API，启动本地服务，并跑后台感知循环。"""

from __future__ import annotations

import asyncio
import contextlib
import logging

import uvicorn

from .agent import Agent
from .api import create_app
from .config import settings
from .models import PetProfile, Species

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("anyfamily.app")


def default_profile() -> PetProfile:
    """MVP 默认宠物档案（真实使用由父母端引导录入创建）。"""
    return PetProfile(
        name="Lucky",
        species=Species.DOG,
        breed="golden_retriever",
        age=3,
        trained_commands=["sit", "come", "wait"],
        preferences={"toys": ["laser", "ball"], "food": ["chicken"]},
        breed_prior={"temperament": "friendly", "activity": "high"},
    )


def build_agent() -> Agent:
    settings.ensure_dirs()
    return Agent(profile=default_profile())


async def _perception_background(agent: Agent, interval_s: float = 5.0) -> None:
    """后台周期性感知，驱动能动 Agent 的自主闭环。"""
    while True:
        with contextlib.suppress(Exception):
            await agent.perceive_once()
        await asyncio.sleep(interval_s)


def main() -> None:
    agent = build_agent()
    app = create_app(agent)

    @app.on_event("startup")
    async def _startup() -> None:
        app.state.perception_task = asyncio.create_task(_perception_background(agent))
        logger.info("后台感知循环已启动")

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        task = getattr(app.state, "perception_task", None)
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    url = f"http://{settings.host}:{settings.port}"
    logger.info("启动 Any-Family 服务 %s （Web 控制台直接打开此地址）", url)
    if settings.open_browser:
        import threading
        import webbrowser

        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
