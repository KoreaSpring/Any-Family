"""LLM 接入层：真实可用的双后端（OpenAI 兼容 / 本地 Ollama），不可用时回退。

设计目标：
- 填了 API Key（OpenAI 兼容，含国内兼容服务）→ 用云端模型。
- 装了本地 Ollama → 用本地模型，数据不出门。
- 两者都没有 → NullProvider，上层自动回退规则版，保证无网也能跑通。

用标准库 urllib 实现 HTTP，避免强依赖；用 asyncio.to_thread 包装以不阻塞事件循环。
"""

from __future__ import annotations

import abc
import asyncio
import json
import logging
import urllib.error
import urllib.request

from .config import settings

logger = logging.getLogger("anyfamily.llm")

Message = dict[str, str]


class LLMProvider(abc.ABC):
    """统一的对话补全接口。"""

    name = "base"

    @property
    def available(self) -> bool:
        return True

    @abc.abstractmethod
    async def chat(self, messages: list[Message], temperature: float = 0.4) -> str:
        """返回模型文本回复。失败应抛异常，由调用方决定是否回退。"""


class NullProvider(LLMProvider):
    """占位：不可用，强制上层走规则回退。"""

    name = "none"

    @property
    def available(self) -> bool:
        return False

    async def chat(self, messages: list[Message], temperature: float = 0.4) -> str:
        raise RuntimeError("LLM 未配置")


class OpenAICompatProvider(LLMProvider):
    """OpenAI 兼容 /chat/completions（OpenAI、国内兼容服务、本地 vLLM 等皆可）。"""

    name = "openai"

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[Message], temperature: float = 0.4) -> str:
        return await asyncio.to_thread(self._chat_sync, messages, temperature)

    def _chat_sync(self, messages: list[Message], temperature: float) -> str:
        body = json.dumps(
            {"model": self.model, "messages": messages, "temperature": temperature}
        ).encode()
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.loads(r.read())
        return data["choices"][0]["message"]["content"].strip()


class OllamaProvider(LLMProvider):
    """本地 Ollama /api/chat。数据不出门。"""

    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @property
    def available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    async def chat(self, messages: list[Message], temperature: float = 0.4) -> str:
        return await asyncio.to_thread(self._chat_sync, messages, temperature)

    def _chat_sync(self, messages: list[Message], temperature: float) -> str:
        body = json.dumps(
            {"model": self.model, "messages": messages, "stream": False,
             "options": {"temperature": temperature}}
        ).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/chat", data=body,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.loads(r.read())
        return data["message"]["content"].strip()


def build_provider() -> LLMProvider:
    """按配置构造 Provider；不可用时返回 NullProvider。"""
    backend = settings.llm_backend.lower()
    if backend == "openai":
        p: LLMProvider = OpenAICompatProvider(
            settings.llm_base_url, settings.llm_api_key, settings.llm_model, settings.llm_timeout_s
        )
    elif backend == "ollama":
        base = settings.llm_base_url if settings.llm_base_url.startswith("http://localhost") \
            else "http://localhost:11434"
        p = OllamaProvider(base, settings.llm_model, settings.llm_timeout_s)
    else:
        p = NullProvider()

    if not p.available:
        logger.info("LLM 后端 '%s' 不可用，回退规则版。", backend)
        return NullProvider()
    logger.info("LLM 后端已就绪: %s (%s)", p.name, settings.llm_model)
    return p
