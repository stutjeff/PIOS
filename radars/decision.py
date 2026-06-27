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


def latest_pios_decision() -> PiosDecision:
    with db_session() as session:
        rows = session.execute(
            select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(5)
        ).scalars().all()

    if not rows:
        return PiosDecision(0.0, "gray", "514", "尚無雷達結果；先抓資料，再執行雷達。")

    scores = []
    for row in rows:
        if row.score and row.score > 0:
            scores.append(float(row.score))
        else:
            scores.append(LEVEL_WEIGHT.get(row.level, 50.0))

    score = round(sum(scores) / len(scores), 2)
    if score >= 66:
        return PiosDecision(score, "red", "433", "PIOS 總壓力進入紅區；進入 433 檢查流程。")
    if score >= 36:
        return PiosDecision(score, "yellow", "514", "PIOS 總壓力偏中性偏熱；維持 514，但提高觀察。")
    return PiosDecision(score, "green", "514", "PIOS 總壓力低；維持 514，照規則走。")
