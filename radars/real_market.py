from __future__ import annotations

from sqlalchemy import select

from radars.base import Radar, RadarResult
from storage.db import db_session
from storage.models import MarketSnapshot


def _latest_value(symbol: str, metric: str) -> float | None:
    with db_session() as session:
        row = session.execute(select(MarketSnapshot).where(MarketSnapshot.symbol == symbol, MarketSnapshot.metric == metric).order_by(MarketSnapshot.captured_at.desc()).limit(1)).scalar_one_or_none()
    return float(row.value) if row and row.value is not None else None


def _latest_values(symbol: str, metric: str, limit: int = 3) -> list[float]:
    with db_session() as session:
        rows = session.execute(select(MarketSnapshot).where(MarketSnapshot.symbol == symbol, MarketSnapshot.metric == metric).order_by(MarketSnapshot.captured_at.desc()).limit(limit)).scalars().all()
    return [float(r.value) for r in rows if r.value is not None]


def _change_score(symbol: str, label: str, inverse: bool = False) -> tuple[str, float] | None:
    vals = _latest_values(symbol, "close", 2)
    if len(vals) < 2 or vals[1] == 0:
        return None
    chg = (vals[0] / vals[1] - 1) * 100
    pressure = 45 - chg * 6
    if inverse:
        pressure = 45 + chg * 6
    return (f"{label} {chg:+.2f}%", max(10, min(90, pressure)))


class RealMarketPressureRadar(Radar):
    name = "real_market_pressure"

    def evaluate(self) -> RadarResult:
        components: list[tuple[str, float]] = []
        vix = _latest_value("^VIX", "close")
        if vix is not None:
            components.append((f"VIX {vix:.2f}", 20 if vix < 18 else 45 if vix < 25 else 70 if vix < 35 else 90))
        for symbol, label, inverse in [
            ("QQQ", "QQQ", False), ("SPY", "SPY", False), ("IWM", "IWM", False), ("SOXX", "SOXX", False),
            ("TLT", "TLT", False), ("UUP", "美元UUP", True), ("GLD", "黃金GLD", True),
            ("USO", "原油USO", True), ("CPER", "銅CPER", False), ("BTC-USD", "BTC", False),
        ]:
            item = _change_score(symbol, label, inverse=inverse)
            if item:
                components.append(item)
        if not components:
            return RadarResult(self.name, "gray", 0, "正式市場雷達尚無足夠資料；先抓取市場資料。")
        score = round(sum(v for _, v in components) / len(components), 2)
        detail = "；".join(k for k, _ in components[:8])
        if score >= 66:
            return RadarResult(self.name, "red", score, f"正式市場壓力 {score}：{detail}。啟動 433 檢查。")
        if score >= 36:
            return RadarResult(self.name, "yellow", score, f"正式市場壓力 {score}：{detail}。維持 514，但提高觀察。")
        return RadarResult(self.name, "green", score, f"正式市場壓力 {score}：{detail}。維持 514。")


class TaiwanCoreRadar(Radar):
    name = "taiwan_core_watch"

    def evaluate(self) -> RadarResult:
        watched = ["00670L.TW", "00662.TW", "00865B.TW", "2002.TW"]
        available = [s for s in watched if _latest_value(s, "close") is not None]
        twse_available = [s for s in ["00670L", "00662", "00865B", "2002"] if _latest_value(s, "official_avg_or_close") is not None]
        coverage = max(len(available), len(twse_available))
        if coverage == 0:
            return RadarResult(self.name, "gray", 0, "台股核心觀察尚無報價資料。")
        score = 25 if coverage >= 4 else 35 if coverage >= 3 else 50
        level = "green" if score < 36 else "yellow"
        return RadarResult(level=level, radar_name=self.name, score=score, summary=f"台股核心追蹤取得 {coverage}/4；可監控 00662 / 00670L / 00865B / 2002，後續接融資與法人。")
