from __future__ import annotations

from sqlalchemy import select

from radars.base import Radar, RadarResult
from storage.db import db_session
from storage.models import MarketSnapshot


def _latest_value(symbol: str, metric: str) -> float | None:
    with db_session() as session:
        row = session.execute(
            select(MarketSnapshot)
            .where(MarketSnapshot.symbol == symbol, MarketSnapshot.metric == metric)
            .order_by(MarketSnapshot.captured_at.desc())
            .limit(1)
        ).scalar_one_or_none()
    return float(row.value) if row and row.value is not None else None


def _latest_values(symbol: str, metric: str, limit: int = 3) -> list[float]:
    with db_session() as session:
        rows = session.execute(
            select(MarketSnapshot)
            .where(MarketSnapshot.symbol == symbol, MarketSnapshot.metric == metric)
            .order_by(MarketSnapshot.captured_at.desc())
            .limit(limit)
        ).scalars().all()
    return [float(r.value) for r in rows if r.value is not None]


class RealMarketPressureRadar(Radar):
    name = "real_market_pressure"

    def evaluate(self) -> RadarResult:
        components: list[tuple[str, float]] = []

        vix = _latest_value("^VIX", "close")
        if vix is not None:
            if vix < 18:
                score = 20
            elif vix < 25:
                score = 45
            elif vix < 35:
                score = 70
            else:
                score = 90
            components.append((f"VIX {vix:.2f}", score))

        qqq = _latest_values("QQQ", "close", 2)
        if len(qqq) >= 2 and qqq[1] != 0:
            pct = (qqq[0] / qqq[1] - 1) * 100
            if pct >= 1:
                score = 20
            elif pct >= -1:
                score = 35
            elif pct >= -3:
                score = 60
            else:
                score = 80
            components.append((f"QQQ latest change {pct:.2f}%", score))

        tlt = _latest_values("TLT", "close", 2)
        if len(tlt) >= 2 and tlt[1] != 0:
            pct = (tlt[0] / tlt[1] - 1) * 100
            # TLT 大跌通常代表利率壓力升高。
            if pct >= 0:
                score = 25
            elif pct >= -1:
                score = 40
            elif pct >= -2:
                score = 60
            else:
                score = 78
            components.append((f"TLT latest change {pct:.2f}%", score))

        if not components:
            return RadarResult(self.name, "gray", 0, "正式市場雷達尚無足夠資料。")

        avg = round(sum(v for _, v in components) / len(components), 2)
        detail = "；".join(label for label, _ in components)
        if avg >= 66:
            return RadarResult(self.name, "red", avg, f"正式市場壓力 {avg}：{detail}。檢查 433 條件。")
        if avg >= 36:
            return RadarResult(self.name, "yellow", avg, f"正式市場壓力 {avg}：{detail}。維持 514，提高觀察。")
        return RadarResult(self.name, "green", avg, f"正式市場壓力 {avg}：{detail}。維持 514。")


class TaiwanCoreRadar(Radar):
    name = "taiwan_core_watch"

    def evaluate(self) -> RadarResult:
        watched = ["00670L.TW", "00662.TW", "00865B.TW", "2002.TW"]
        available = [s for s in watched if _latest_value(s, "close") is not None]
        if not available:
            return RadarResult(self.name, "gray", 0, "台股核心觀察尚無 Yahoo 收盤資料，先看 TWSE 官方資料。")
        score = 30 if len(available) >= 3 else 45
        return RadarResult(
            self.name,
            "green" if score < 36 else "yellow",
            score,
            f"台股核心追蹤已取得 {len(available)}/{len(watched)} 個 Yahoo 報價；可用於後續 00662 / 00670L / 00865B 偏離監控。",
        )
