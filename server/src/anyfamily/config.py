"""运行时配置。

本地优先：所有数据默认落在本机 data_dir，不出家门。
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANYFAMILY_", env_file=".env")

    # 数据根目录（事件时间线 / 画像 / 媒体片段）。本地优先，隐私不出门。
    data_dir: Path = Path("./data")

    # HTTP 服务
    host: str = "127.0.0.1"
    port: int = 8080

    # 是否启用"主动陪伴"决策（宠物焦虑/无聊时 agent 主动调硬件逗玩/安抚）
    proactive_enabled: bool = True

    # 决策是否使用 LLM（关闭时走纯规则 Planner，保证无网也能跑通闭环）
    use_llm_planner: bool = False

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "media").mkdir(parents=True, exist_ok=True)


settings = Settings()
