from __future__ import annotations

from dataclasses import dataclass
import json
from datetime import datetime, timedelta
from sqlalchemy import select

from storage.db import db_session
from storage.models import RadarSignal, PiosScoreHistory


@dataclass(frozen=True)
class PiosComponent:
    name: str
    score: float
    level: str
    weight: float
    summary: str


@dataclass(frozen=True)
class PiosDecision:
    score: float
    level: str
    mode: str
    summary: str
    components: list[PiosComponent]


LEVEL_WEIGHT = {"green": 25.0, "yellow": 55.0, "red": 85.0, "gray": 50.0, "watch": 50.0}
RADAR_WEIGHTS = {
    "real_market_pressure": 0.30,
    "news_radar": 0.25,
    "taiwan_core_watch": 0.15,
    "chengxin_watch": 0.15,
    "market_pressure": 0.05,
}


def _latest_signals(limit: int = 80) -> list[RadarSignal]:
    with db_session() as session:
        return list(session.execute(select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(limit)).scalars().all())


def latest_pios_decision(save_history: bool = False) -> PiosDecision:
    rows = _latest_signals()
    if not rows:
        return PiosDecision(0.0, "gray", "514", "尚無雷達結果；先抓資料，再執行雷達。", [])

    latest_by_name: dict[str, RadarSignal] = {}
    for row in rows:
        latest_by_name.setdefault(row.radar_name, row)

    weighted_sum = 0.0
    total_weight = 0.0
    components: list[PiosComponent] = []
    for name, weight in RADAR_WEIGHTS.items():
        row = latest_by_name.get(name)
        if not row:
            continue
        score = float(row.score) if row.score is not None and row.score > 0 else LEVEL_WEIGHT.get(row.level, 50.0)
        weighted_sum += score * weight
        total_weight += weight
        components.append(PiosComponent(name, round(score, 2), row.level, weight, row.summary))

    if total_weight == 0:
        return PiosDecision(0.0, "gray", "514", "尚無可用雷達。", [])

    pressure = round(weighted_sum / total_weight, 2)
    if pressure >= 68:
        decision = PiosDecision(pressure, "red", "433", "總壓力進入紅區；啟動 433 檢查，先求活著，再談獲利。", components)
    elif pressure >= 45:
        decision = PiosDecision(pressure, "yellow", "514", "總壓力偏中性偏熱；維持 514，但提高觀察頻率。", components)
    else:
        decision = PiosDecision(pressure, "green", "514", "總壓力低；維持 514，照規則走。", components)

    if save_history:
        save_pios_decision(decision)
    return decision


def save_pios_decision(decision: PiosDecision) -> None:
    payload = [c.__dict__ for c in decision.components]
    with db_session() as session:
        last = session.execute(select(PiosScoreHistory).order_by(PiosScoreHistory.created_at.desc()).limit(1)).scalar_one_or_none()
        if last and last.created_at and last.created_at >= datetime.utcnow() - timedelta(minutes=3):
            last.score = decision.score
            last.level = decision.level
            last.mode = decision.mode
            last.summary = decision.summary
            last.components_json = json.dumps(payload, ensure_ascii=False)
            return
        session.add(PiosScoreHistory(score=decision.score, level=decision.level, mode=decision.mode, summary=decision.summary, components_json=json.dumps(payload, ensure_ascii=False)))
