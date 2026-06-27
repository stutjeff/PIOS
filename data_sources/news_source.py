from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
import json
import os
import re
from datetime import timedelta
from typing import Protocol
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


@dataclass(frozen=True)
class NewsPoint:
    source: str
    title: str
    url: str
    publisher: str | None = None
    query: str | None = None
    symbols: str | None = None
    sentiment: float | None = None
    summary: str | None = None
    published_at: datetime | None = None
    captured_at: datetime | None = None


class NewsSource(Protocol):
    name: str

    def fetch(self) -> list[NewsPoint]:
        ...


def _open_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "PIOS/4.0"})
    with urlopen(req, timeout=15) as resp:  # noqa: S310 - controlled public API URLs
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _open_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "PIOS/4.0"})
    with urlopen(req, timeout=15) as resp:  # noqa: S310 - controlled public RSS URL
        return resp.read().decode("utf-8", errors="replace")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value).replace(tzinfo=None)
    except Exception:
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except Exception:
            return None


def _clean(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


class GoogleNewsRSSSource:
    name = "google_news_rss"

    def __init__(self, queries: list[str], per_query_limit: int = 5):
        self.queries = queries
        self.per_query_limit = per_query_limit

    def fetch(self) -> list[NewsPoint]:
        items: list[NewsPoint] = []
        for query in self.queries:
            url = (
                "https://news.google.com/rss/search?"
                + urlencode({"q": query, "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"})
            )
            xml_text = _open_text(url)
            root = ET.fromstring(xml_text)
            for item in root.findall("./channel/item")[: self.per_query_limit]:
                title = _clean(item.findtext("title"))
                link = item.findtext("link") or ""
                source_el = item.find("source")
                publisher = _clean(source_el.text if source_el is not None else None) or None
                published_at = _parse_dt(item.findtext("pubDate"))
                if title and link:
                    items.append(
                        NewsPoint(
                            source=self.name,
                            title=title,
                            url=link,
                            publisher=publisher,
                            query=query,
                            summary=_clean(item.findtext("description"))[:600] or None,
                            published_at=published_at,
                        )
                    )
        return items


class FinnhubNewsSource:
    name = "finnhub_news"

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.api_key = os.getenv("FINNHUB_API_KEY", "").strip()

    def fetch(self) -> list[NewsPoint]:
        if not self.api_key:
            return []
        items: list[NewsPoint] = []
        for symbol in self.symbols:
            today = datetime.utcnow().date()
            start = today - timedelta(days=14)
            url = f"https://finnhub.io/api/v1/company-news?symbol={quote_plus(symbol)}&from={start.isoformat()}&to={today.isoformat()}&token={quote_plus(self.api_key)}"
            data = _open_json(url)
            if not isinstance(data, list):
                continue
            for row in data[:8]:
                title = _clean(row.get("headline"))
                link = row.get("url") or ""
                ts = row.get("datetime")
                published_at = datetime.utcfromtimestamp(ts) if isinstance(ts, (int, float)) else None
                if title and link:
                    items.append(
                        NewsPoint(
                            source=self.name,
                            title=title,
                            url=link,
                            publisher=row.get("source"),
                            symbols=symbol,
                            summary=_clean(row.get("summary"))[:900] or None,
                            published_at=published_at,
                        )
                    )
        return items


class MarketauxNewsSource:
    name = "marketaux_news"

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self.api_key = os.getenv("MARKETAUX_API_KEY", "").strip()

    def fetch(self) -> list[NewsPoint]:
        if not self.api_key:
            return []
        params = urlencode(
            {
                "api_token": self.api_key,
                "symbols": ",".join(self.symbols),
                "language": "en",
                "limit": "20",
            }
        )
        data = _open_json(f"https://api.marketaux.com/v1/news/all?{params}")
        rows = data.get("data", []) if isinstance(data, dict) else []
        items: list[NewsPoint] = []
        for row in rows:
            title = _clean(row.get("title"))
            link = row.get("url") or ""
            entities = row.get("entities") or []
            symbols = ",".join(sorted({str(e.get("symbol")) for e in entities if e.get("symbol")})) or None
            sentiment = None
            scores = [e.get("sentiment_score") for e in entities if isinstance(e.get("sentiment_score"), (int, float))]
            if scores:
                sentiment = round(sum(scores) / len(scores), 4)
            if title and link:
                items.append(
                    NewsPoint(
                        source=self.name,
                        title=title,
                        url=link,
                        publisher=(row.get("source") or ""),
                        symbols=symbols,
                        sentiment=sentiment,
                        summary=_clean(row.get("description"))[:900] or None,
                        published_at=_parse_dt(row.get("published_at")),
                    )
                )
        return items
