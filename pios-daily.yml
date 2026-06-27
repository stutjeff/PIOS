from __future__ import annotations

from datetime import datetime

from data_sources.base import DataPoint, SourceRunResult
from storage.db import db_session
from storage.models import MarketSnapshot, SourceRun


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


def save_source_run(result: SourceRunResult) -> None:
    with db_session() as session:
        session.add(
            SourceRun(
                source=result.source,
                ok=result.ok,
                count=result.count,
                error=result.error,
                started_at=result.started_at,
                finished_at=result.finished_at,
            )
        )
