"""记忆层：事件时间线 + 作息画像（本地存储）。

- 订阅所有事件，追加写入当日 JSONL 时间线（本地优先，隐私不出门）。
- 提供今日概览、时间线查询、简单作息画像统计。
- 存储解读(Interpretation)与健康提示(HealthAlert)供接口与 3D 形态图使用。
"""

from __future__ import annotations

import json
import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .config import settings
from .events import Event, EventType
from .models import HealthAlert, Interpretation

logger = logging.getLogger("anyfamily.memory")


def _day_key(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%Y-%m-%d")


class MemoryStore:
    def __init__(self) -> None:
        settings.ensure_dirs()
        self.root = settings.data_dir
        self._interpretations: list[Interpretation] = []
        self._health: list[HealthAlert] = []

    # ---- 事件总线挂钩：订阅所有事件做落地 ----
    async def on_event(self, event: Event) -> None:
        self._append_timeline(event)

    def _timeline_path(self, ts: float) -> Path:
        d = self.root / "timeline"
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{_day_key(ts)}.jsonl"

    def _append_timeline(self, event: Event) -> None:
        path = self._timeline_path(event.ts)
        with path.open("a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")

    # ---- 查询 ----
    def read_timeline(self, day: str | None = None, limit: int = 200) -> list[dict]:
        day = day or _day_key(time.time())
        path = self.root / "timeline" / f"{day}.jsonl"
        if not path.exists():
            return []
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        return rows[-limit:]

    def today_overview(self, pet_id: str) -> dict:
        """今日概览：活动分布、发声次数、执行动作次数等。"""
        rows = self.read_timeline(limit=10000)
        rows = [r for r in rows if r.get("pet_id") in (pet_id, None)]

        activities: Counter[str] = Counter()
        vocal_count = 0
        actions: Counter[str] = Counter()
        for r in rows:
            etype = r.get("type")
            payload = r.get("payload", {})
            if etype == EventType.PET_ACTIVITY.value:
                activities[payload.get("activity", "unknown")] += 1
            elif etype == EventType.PET_VOCAL.value:
                vocal_count += 1
            elif etype == EventType.ACTION_RESULT.value and payload.get("ok"):
                actions[payload.get("capability", "unknown")] += 1

        summary = self._summarize(activities, vocal_count, actions)
        return {
            "pet_id": pet_id,
            "day": _day_key(time.time()),
            "activities": dict(activities),
            "vocal_count": vocal_count,
            "actions": dict(actions),
            "summary": summary,
        }

    @staticmethod
    def _summarize(activities: Counter[str], vocal: int, actions: Counter[str]) -> str:
        if not activities and not vocal and not actions:
            return "今天还没有观察到明显活动。"
        parts: list[str] = []
        if activities:
            top = activities.most_common(1)[0][0]
            label = {
                "eating": "在吃东西", "sleeping": "在睡觉", "playing": "在玩",
                "restless": "有点躁动", "idle": "比较安静", "moving": "在走动",
            }.get(top, top)
            parts.append(f"大部分时间{label}")
        if vocal:
            parts.append(f"叫了约 {vocal} 次")
        if actions:
            did = "、".join(f"{k}×{v}" for k, v in actions.items())
            parts.append(f"陪伴设备执行了：{did}")
        return "；".join(parts) + "。"

    # ---- 解读与健康提示 ----
    def add_interpretation(self, intp: Interpretation) -> None:
        self._interpretations.append(intp)

    def recent_interpretations(self, pet_id: str, limit: int = 20) -> list[Interpretation]:
        items = [i for i in self._interpretations if i.pet_id == pet_id]
        return items[-limit:]

    def add_health_alert(self, alert: HealthAlert) -> None:
        self._health.append(alert)

    def health_alerts(self, pet_id: str) -> list[HealthAlert]:
        return [h for h in self._health if h.pet_id == pet_id]
