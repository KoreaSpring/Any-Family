"""类型化事件。

各层通过事件总线交换这些事件，彼此解耦：
  perception.*  感知层产出（宠物在不在/在干嘛/叫声/情绪）
  decision.*    决策层产出（对需求的解读、计划）
  action.*      执行器动作请求与反馈（驱动硬件：说话/看/逗玩/投食）
  health.*      健康提示
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from .models import EmotionVA


def _now() -> float:
    return time.time()


def _uid() -> str:
    return uuid.uuid4().hex[:12]


class EventType(str, Enum):
    # 感知
    PET_PRESENCE = "perception.presence"      # 宠物进/出画面
    PET_ACTIVITY = "perception.activity"      # 在吃/睡/玩/闹/静止
    PET_VOCAL = "perception.vocal"            # 发声（叫/呜咽/喘）
    PET_EMOTION = "perception.emotion"        # 情绪信号（VA）
    # 决策
    INTERPRETATION = "decision.interpretation"  # 对状态/需求的解读
    PLAN = "decision.plan"                       # 生成的行动计划
    # 执行器
    ACTION_REQUEST = "action.request"         # 请求执行一个设备动作
    ACTION_RESULT = "action.result"           # 动作执行反馈
    # 健康
    HEALTH_ALERT = "health.alert"


class Event(BaseModel):
    """所有事件的基类。"""

    id: str = Field(default_factory=_uid)
    type: EventType
    ts: float = Field(default_factory=_now)
    pet_id: str | None = None
    source: str = "unknown"          # 产生该事件的组件
    payload: dict[str, Any] = Field(default_factory=dict)
    # 关联的媒体片段（截图/短视频/音频），相对 data_dir/media 的路径
    media: list[str] = Field(default_factory=list)


# ---- 便捷构造器（让各层产事件时意图清晰）----

Activity = Literal["eating", "sleeping", "playing", "restless", "idle", "moving"]


def presence_event(pet_id: str, present: bool, source: str, **payload: Any) -> Event:
    return Event(
        type=EventType.PET_PRESENCE,
        pet_id=pet_id,
        source=source,
        payload={"present": present, **payload},
    )


def activity_event(pet_id: str, activity: Activity, source: str, **payload: Any) -> Event:
    return Event(
        type=EventType.PET_ACTIVITY,
        pet_id=pet_id,
        source=source,
        payload={"activity": activity, **payload},
    )


def vocal_event(pet_id: str, kind: str, emotion: EmotionVA, source: str, **payload: Any) -> Event:
    return Event(
        type=EventType.PET_VOCAL,
        pet_id=pet_id,
        source=source,
        payload={"kind": kind, "emotion": emotion.model_dump(), **payload},
    )


def action_request(pet_id: str, capability: str, args: dict[str, Any], source: str) -> Event:
    """请求某个设备能力执行动作：capability ∈ speak/play/feed/camera 等。"""
    return Event(
        type=EventType.ACTION_REQUEST,
        pet_id=pet_id,
        source=source,
        payload={"capability": capability, "args": args},
    )


def action_result(pet_id: str, capability: str, ok: bool, source: str, **payload: Any) -> Event:
    return Event(
        type=EventType.ACTION_RESULT,
        pet_id=pet_id,
        source=source,
        payload={"capability": capability, "ok": ok, **payload},
    )
