"""核心领域模型（跨层共享的数据结构）。

与 docs/PRODUCT.md 第 7 节的跨端契约保持一致。
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _now() -> float:
    return time.time()


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Species(str, Enum):
    DOG = "dog"
    CAT = "cat"


class EmotionVA(BaseModel):
    """连续的"效价-唤醒度"情绪坐标（见 RESEARCH.md 第 5 章）。

    valence: 负面(-1) ↔ 正面(+1)
    arousal: 平静(0) ↔ 激动(1)
    """

    valence: float = 0.0
    arousal: float = 0.0


class PetProfile(BaseModel):
    """宠物档案。录入时创建，个体画像随观测持续校准。"""

    id: str = Field(default_factory=lambda: _uid("pet"))
    name: str
    species: Species = Species.DOG
    breed: str | None = None
    age: float | None = None
    sex: str | None = None
    neutered: bool | None = None
    weight_kg: float | None = None

    habits: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] = Field(default_factory=dict)
    trained_commands: list[str] = Field(default_factory=list)
    voice_profile_id: str | None = None

    # 品种先验 vs 个体观测的动态权重：观测越多越小（见 RESEARCH.md 第 6 章）
    breed_prior: dict[str, Any] = Field(default_factory=dict)
    individual_profile: dict[str, Any] = Field(default_factory=dict)
    prior_weight: float = 0.8

    created_at: float = Field(default_factory=_now)


class Interpretation(BaseModel):
    """对宠物状态/需求的解读（"听懂我"的统一输出）。

    始终带证据与置信度——我们做解读，不做"翻译"。
    """

    id: str = Field(default_factory=lambda: _uid("intp"))
    ts: float = Field(default_factory=_now)
    pet_id: str
    state: EmotionVA = Field(default_factory=EmotionVA)
    label: str
    confidence: float = 0.5
    evidence: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=list)


class Severity(str, Enum):
    WARN = "warn"
    URGENT = "urgent"


class HealthAlert(BaseModel):
    """健康提示（3D 形态图标注来源）。提示而非诊断。"""

    id: str = Field(default_factory=lambda: _uid("health"))
    ts: float = Field(default_factory=_now)
    pet_id: str
    region: str
    severity: Severity = Severity.WARN
    finding: str
    evidence: list[str] = Field(default_factory=list)
    advice: str = ""
    disclaimer: str = "本提示不构成诊断，请以兽医检查为准。"
