from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy import select

from data_sources.news_source import FinnhubNewsSource, GoogleNewsRSSSource, MarketauxNewsSource, NewsPoint, NewsSource
from data_sources.base import SourceRunResult
from services.ingestion import save_source_run
from storage.db import db_session
from storage.models import NewsItem
from services.news_intelligence import classify_news, enrich_recent_news


@dataclass
class NewsRunResult:
    source: str
    ok: bool
    count: int = 0
    error: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None


def save_news_items(items: list[NewsPoint]) -> int:
    saved = 0
    with db_session() as session:
        for item in items:
            exists = session.execute(
                select(NewsItem.id).where(NewsItem.source == item.source, NewsItem.url == item.url).limit(1)
            ).scalar_one_or_none()
            if exists:
                continue
            profile = classify_news(item.title, item.query, item.publisher)
            session.add(
                NewsItem(
                    source=item.source,
                    title=item.title,
                    url=item.url,
                    publisher=item.publisher,
                    query=item.query,
                    symbols=item.symbols,
                    sentiment=item.sentiment,
                    summary=item.summary or profile.short_summary,
                    category=profile.category,
                    related_symbols=profile.related_symbols,
                    impact_score=profile.impact_score,
                    risk_score=profile.risk_score,
                    published_at=item.published_at,
                    captured_at=item.captured_at or datetime.utcnow(),
                )
            )
            saved += 1
    return saved


class NewsSourceManager:
    def __init__(self, sources: list[NewsSource]):
        self.sources = sources

    def fetch_all(self) -> list[NewsRunResult]:
        results: list[NewsRunResult] = []
        for source in self.sources:
            started = datetime.utcnow()
            try:
                items = source.fetch()
                count = save_news_items(items)
                result = NewsRunResult(source.name, True, count, None, started, datetime.utcnow())
            except Exception as exc:  # noqa: BLE001
                result = NewsRunResult(source.name, False, 0, str(exc)[:1000], started, datetime.utcnow())
            save_source_run(
                SourceRunResult(
                    source=f"news:{result.source}",
                    ok=result.ok,
                    count=result.count,
                    error=result.error,
                    started_at=result.started_at,
                    finished_at=result.finished_at,
                )
            )
            results.append(result)
        enrich_recent_news()
        return results


def build_default_news_manager() -> NewsSourceManager:
    queries = [
        "成信 6969",
        "台股 融資 外資",
        "QQQ Nasdaq Fed",
        "00662 ETF",
        "00670L 台股正二",
        "00865B 美債",
        "AI data center power market",
    ]
    symbols = ["QQQ", "TSM", "NVDA", "TLT"]
    return NewsSourceManager(
        [
            GoogleNewsRSSSource(queries=queries, per_query_limit=4),
            FinnhubNewsSource(symbols=symbols),
            MarketauxNewsSource(symbols=symbols),
        ]
    )
