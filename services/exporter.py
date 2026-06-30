from __future__ import annotations

import pandas as pd
from sqlalchemy import select

from storage.db import db_session
from storage.models import MarketSnapshot, NewsItem, RadarSignal, SourceRun, PiosScoreHistory, AlertEvent


def table_to_frame(name: str, limit: int = 500) -> pd.DataFrame:
    model_map = {
        "market_snapshots": MarketSnapshot,
        "news_items": NewsItem,
        "radar_signals": RadarSignal,
        "source_runs": SourceRun,
        "pios_score_history": PiosScoreHistory,
        "alert_events": AlertEvent,
    }
    model = model_map[name]
    order_col = getattr(model, "created_at", None) or getattr(model, "captured_at", None) or getattr(model, "started_at", None) or model.id
    with db_session() as session:
        rows = session.execute(select(model).order_by(order_col.desc()).limit(limit)).scalars().all()
    return pd.DataFrame([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])
