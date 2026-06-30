from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy import select

from storage.db import db_session
from storage.models import AlertEvent, NewsItem, RadarSignal


def _exists_recent(session, source: str, title: str, minutes: int = 180) -> bool:
    since = datetime.utcnow() - timedelta(minutes=minutes)
    return session.execute(select(AlertEvent.id).where(AlertEvent.source == source, AlertEvent.title == title, AlertEvent.created_at >= since).limit(1)).scalar_one_or_none() is not None


def generate_alerts() -> int:
    created = 0
    with db_session() as session:
        signals = session.execute(select(RadarSignal).order_by(RadarSignal.created_at.desc()).limit(20)).scalars().all()
        seen = set()
        for s in signals:
            if s.radar_name in seen:
                continue
            seen.add(s.radar_name)
            if s.level in {"red", "yellow"} and float(s.score or 0) >= 45:
                title = f"{s.radar_name}: {s.level} {round(float(s.score or 0), 2)}"
                if not _exists_recent(session, "radar", title):
                    session.add(AlertEvent(source="radar", level=s.level, title=title, detail=s.summary))
                    created += 1

        news = session.execute(select(NewsItem).where(NewsItem.impact_score >= 78).order_by(NewsItem.impact_score.desc()).limit(8)).scalars().all()
        for n in news:
            title = f"高影響新聞：{n.title[:90]}"
            level = "red" if (n.risk_score or 0) >= 65 else "yellow"
            if not _exists_recent(session, "news", title, minutes=720):
                session.add(AlertEvent(source="news", level=level, title=title, detail=f"{n.category}｜影響 {n.impact_score}｜風險 {n.risk_score}｜關聯 {n.related_symbols}"))
                created += 1
    return created
