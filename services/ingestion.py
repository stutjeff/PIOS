from __future__ import annotations

from datetime import datetime

from data_sources.base import DataPoint
from storage.db import db_session
from storage.models import MarketSnapshot


def save_datapoints(points: list[DataPoint]) -> int:
    with db_session() as session:
        for p in points:
            session.add(
                MarketSnapshot(
                    source=p.source,
                    symbol=p.symbol,
                    metric=p.metric,
                    value=p.value,
                    raw_text=p.raw_text,
                    captured_at=p.captured_at or datetime.utcnow(),
                )
            )
        return len(points)
