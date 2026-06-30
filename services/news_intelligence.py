from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from sqlalchemy import select

from storage.db import db_session
from storage.models import NewsItem, RadarSignal


@dataclass(frozen=True)
class NewsProfile:
    category: str
    impact_score: float
    risk_score: float
    related_symbols: str
    short_summary: str
    importance: str


CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("AI資料中心/電力", ["ai", "data center", "資料中心", "數據中心", "電力", "power", "grid", "電網", "nvidia", "nvda"]),
    ("美債/利率", ["bond", "treasury", "yield", "fed", "rate", "美債", "公債", "殖利率", "降息", "升息", "00865b", "tlt"]),
    ("台股ETF/槓桿", ["00670l", "台股正二", "0050", "etf", "加權", "台股"]),
    ("成信6969/CMP回收", ["成信", "6969", "cmp", "污泥", "回收", "循環", "再利用"]),
    ("半導體/AI供應鏈", ["semiconductor", "半導體", "tsmc", "台積", "封裝", "sox", "晶片"]),
    ("能源/原物料", ["oil", "copper", "gold", "原油", "銅", "黃金", "能源"]),
    ("美股科技/QQQ", ["qqq", "nasdaq", "s&p", "microsoft", "apple", "google", "meta", "tesla"]),
]

RISK_WORDS = ["slip", "falls", "跌", "下滑", "風險", "壓力", "警告", "衰退", "違約", "虧損", "升息", "通膨", "戰爭"]
POS_WORDS = ["surge", "gain", "上漲", "成長", "受惠", "利多", "突破", "合作", "agreement", "擴建", "增長"]

SYMBOL_RULES: list[tuple[str, list[str]]] = [
    ("6969/成信", ["成信", "6969", "cmp", "污泥", "回收", "再利用"]),
    ("00662", ["00662", "nasdaq", "科技", "qqq"]),
    ("00670L", ["00670l", "台股正二", "加權", "台股"]),
    ("00865B/TLT", ["00865b", "美債", "公債", "tlt", "treasury", "bond", "yield"]),
    ("QQQ", ["qqq", "nasdaq", "microsoft", "apple", "nvidia", "nvda", "ai"]),
    ("電網：中興電/華城/士電", ["電力", "電網", "grid", "power", "data center", "資料中心", "數據中心"]),
    ("AI散熱：台達電/奇鋐/健策", ["data center", "資料中心", "散熱", "cooling", "ai"]),
]


def _match_any(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w.lower() in t for w in words)


def classify_news(title: str, query: str | None = None, publisher: str | None = None) -> NewsProfile:
    text = " ".join([title or "", query or "", publisher or ""]).lower()

    category = "一般財經"
    for cat, words in CATEGORY_RULES:
        if _match_any(text, words):
            category = cat
            break

    related: list[str] = []
    for symbol_label, words in SYMBOL_RULES:
        if _match_any(text, words):
            related.append(symbol_label)

    risk_hits = sum(1 for w in RISK_WORDS if w.lower() in text)
    pos_hits = sum(1 for w in POS_WORDS if w.lower() in text)

    # 影響力不是投資建議，只是「值得看」分數。
    impact = 40.0
    if category != "一般財經":
        impact += 18
    impact += min(len(related) * 7, 21)
    impact += min(pos_hits * 4, 12)
    impact += min(risk_hits * 5, 15)
    impact = max(0, min(100, impact))

    risk = 35.0 + min(risk_hits * 12, 40) - min(pos_hits * 5, 15)
    risk = max(0, min(100, risk))

    importance = "★★★★★" if impact >= 80 else "★★★★☆" if impact >= 68 else "★★★☆☆" if impact >= 55 else "★★☆☆☆"

    relation_text = "、".join(related) if related else "暫無明確對應標的"
    polarity = "偏風險" if risk_hits > pos_hits else "偏利多" if pos_hits > risk_hits else "中性觀察"
    short_summary = f"分類：{category}；影響：{relation_text}；語氣：{polarity}。"

    return NewsProfile(
        category=category,
        impact_score=round(impact, 2),
        risk_score=round(risk, 2),
        related_symbols=relation_text,
        short_summary=short_summary,
        importance=importance,
    )


def enrich_recent_news(limit: int = 120) -> int:
    """用規則引擎補上新聞分類、摘要、影響分數。無需 API key。"""
    updated = 0
    with db_session() as session:
        rows = session.execute(
            select(NewsItem).order_by(NewsItem.captured_at.desc()).limit(limit)
        ).scalars().all()
        for item in rows:
            profile = classify_news(item.title, item.query, item.publisher)
            changed = False
            if getattr(item, "category", None) != profile.category:
                item.category = profile.category
                changed = True
            if getattr(item, "impact_score", None) != profile.impact_score:
                item.impact_score = profile.impact_score
                changed = True
            if getattr(item, "risk_score", None) != profile.risk_score:
                item.risk_score = profile.risk_score
                changed = True
            if getattr(item, "related_symbols", None) != profile.related_symbols:
                item.related_symbols = profile.related_symbols
                changed = True
            if not item.summary or item.summary != profile.short_summary:
                item.summary = profile.short_summary
                changed = True
            if changed:
                updated += 1
    return updated


def build_personal_news_digest(limit: int = 8) -> list[NewsItem]:
    with db_session() as session:
        rows = session.execute(
            select(NewsItem)
            .order_by(NewsItem.impact_score.desc().nullslast(), NewsItem.published_at.desc().nullslast(), NewsItem.captured_at.desc())
            .limit(limit)
        ).scalars().all()
        return list(rows)
