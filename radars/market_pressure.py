from __future__ import annotations

from sqlalchemy import select

from radars.base import Radar, RadarResult
from storage.db import db_session
from storage.models import MarketSnapshot


class MarketPressureRadar(Radar):
    name = "market_pressure"

    def evaluate(self) -> RadarResult:
        metrics = ["momentum_score", "margin_pressure", "credit_spread_pressure"]
        values: list[float] = []
        with db_session() as session:
            for metric in metrics:
                stmt = (
                    select(MarketSnapshot)
                    .where(MarketSnapshot.metric == metric)
                    .order_by(MarketSnapshot.captured_at.desc())
                    .limit(1)
                )
                row = session.execute(stmt).scalar_one_or_none()
                if row and row.value is not None:
                    values.append(float(row.value))

        if not values:
            return RadarResult(self.name, "gray", 0, "尚無足夠資料，先不要亂判斷。")

        score = round(sum(values) / len(values), 2)
        if score >= 66:
            level = "red"
            summary = f"壓力分數 {score}，進入警戒區；系統建議檢查 514 → 433 條件。"
        elif score >= 36:
            level = "yellow"
            summary = f"壓力分數 {score}，偏中性偏熱；維持 514，但提高觀察頻率。"
        else:
            level = "green"
            summary = f"壓力分數 {score}，市場壓力低；照計畫走，不用自己嚇自己。"
        return RadarResult(self.name, level, score, summary)
