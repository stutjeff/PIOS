from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy import select

from radars.base import RadarResult, Radar
from storage.db import db_session
from storage.models import NewsItem

HOT_KEYWORDS = [
    "暴跌", "崩盤", "違約", "衰退", "crash", "default", "recession", "bankruptcy",
    "升息", "通膨", "inflation", "rate hike", "war", "戰爭",
]
POSITIVE_KEYWORDS = ["合作", "增資", "許可", "驗證", "growth", "approval", "partnership", "record"]


class NewsRadar(Radar):
    name = "news_radar"

    def evaluate(self) -> RadarResult:
        since = datetime.utcnow() - timedelta(days=3)
        with db_session() as session:
            rows = session.execute(
                select(NewsItem).where(NewsItem.captured_at >= since).order_by(NewsItem.captured_at.desc()).limit(80)
            ).scalars().all()

        if not rows:
            return RadarResult(self.name, "gray", 0, "新聞雷達尚無資料；可先抓 Google News RSS，API key 之後再補。")

        hot_hits = 0
        positive_hits = 0
        sentiment_scores: list[float] = []
        watched_hits: dict[str, int] = {}
        for row in rows:
            text = f"{row.title} {row.summary or ''}".lower()
            if any(k.lower() in text for k in HOT_KEYWORDS):
                hot_hits += 1
            if any(k.lower() in text for k in POSITIVE_KEYWORDS):
                positive_hits += 1
            if row.sentiment is not None:
                sentiment_scores.append(float(row.sentiment))
            key = row.query or row.symbols or "general"
            watched_hits[key] = watched_hits.get(key, 0) + 1

        score = 30 + min(hot_hits * 8, 40) - min(positive_hits * 3, 12)
        if sentiment_scores:
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            # Marketaux sentiment 約 -1 到 +1，負面提高壓力。
            score += max(0, -avg_sentiment * 20)
            score -= max(0, avg_sentiment * 8)
        score = round(max(0, min(100, score)), 2)

        top = sorted(watched_hits.items(), key=lambda x: x[1], reverse=True)[:3]
        top_text = "、".join(f"{k}:{v}" for k, v in top)
        summary = f"近三日新聞 {len(rows)} 則；風險詞 {hot_hits}，正面詞 {positive_hits}；熱門追蹤：{top_text}。"
        if score >= 66:
            return RadarResult(self.name, "red", score, f"新聞壓力偏高：{summary}")
        if score >= 36:
            return RadarResult(self.name, "yellow", score, f"新聞壓力中性偏高：{summary}")
        return RadarResult(self.name, "green", score, f"新聞壓力低：{summary}")
