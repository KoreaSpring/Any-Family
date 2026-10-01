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
    open_browser: bool = True  # 启动后自动打开 Web 控制台

    # 是否启用"主动陪伴"决策（宠物焦虑/无聊时 agent 主动调硬件逗玩/安抚）
    proactive_enabled: bool = True

    # 决策是否使用 LLM（关闭或不可用时自动回退纯规则，保证无网也能跑通闭环）
    use_llm_planner: bool = False

    # LLM 后端：openai（OpenAI 兼容，含国内兼容服务）/ ollama（本地）/ none（纯规则）
    llm_backend: str = "none"
    llm_base_url: str = "https://api.openai.com/v1"  # openai 兼容端点
    llm_api_key: str = ""                             # 由环境变量 ANYFAMILY_LLM_API_KEY 提供
    llm_model: str = "gpt-4o-mini"
    llm_timeout_s: float = 20.0

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "media").mkdir(parents=True, exist_ok=True)


settings = Settings()
