from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import select

from storage.db import db_session
from storage.models import RadarSignal


@dataclass(frozen=True)
class PiosDecision:
    score: float
    level: str
    mode: str
    summary: str


LEVEL_WEIGHT = {
    "green": 20.0,
    "yellow": 55.0,
    "red": 85.0,
    "gray": 50.0,
}

RADAR_WEIGHTS = {
    "real_market_pressure": 0.50,
    "taiwan_core_watch": 0.20,
    "chengxin_watch": 0.15,
    "news_radar": 0.15,
    "market_pressure": 0.05,  # mock 對照資料，只給低權重。
}


def latest_pios_decision() -> PiosDecision:
    with db_session() as session:
        rows = session.execute(
            select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(20)
        ).scalars().all()

    if not rows:
        return PiosDecision(0.0, "gray", "514", "尚無雷達結果；先抓資料，再執行雷達。")

    latest_by_name: dict[str, RadarSignal] = {}
    for row in rows:
        latest_by_name.setdefault(row.radar_name, row)

    weighted_sum = 0.0
    total_weight = 0.0
    used = []
    for name, weight in RADAR_WEIGHTS.items():
        row = latest_by_name.get(name)
        if not row:
            continue
        score = float(row.score) if row.score and row.score > 0 else LEVEL_WEIGHT.get(row.level, 50.0)
        weighted_sum += score * weight
        total_weight += weight
        used.append(name)

    if total_weight == 0:
        return PiosDecision(0.0, "gray", "514", "尚無可用雷達。")

    score = round(weighted_sum / total_weight, 2)
    if score >= 66:
        return PiosDecision(score, "red", "433", f"PIOS 加權總壓力進入紅區；啟動 433 檢查。來源：{', '.join(used)}")
    if score >= 36:
        return PiosDecision(score, "yellow", "514", f"PIOS 加權總壓力偏中性偏熱；維持 514，提高觀察。來源：{', '.join(used)}")
    return PiosDecision(score, "green", "514", f"PIOS 加權總壓力低；維持 514。來源：{', '.join(used)}")
