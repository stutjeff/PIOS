from __future__ import annotations

from storage.db import db_session
from storage.models import RadarSignal
from radars.market_pressure import MarketPressureRadar


def run_all_radars() -> list[RadarSignal]:
    radar_classes = [MarketPressureRadar]
    saved: list[RadarSignal] = []
    with db_session() as session:
        for cls in radar_classes:
            result = cls().evaluate()
            signal = RadarSignal(
                radar_name=result.radar_name,
                level=result.level,
                score=result.score,
                summary=result.summary,
            )
            session.add(signal)
            saved.append(signal)
    return saved
