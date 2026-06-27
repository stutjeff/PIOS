from __future__ import annotations

from radars.base import RadarResult
from radars.chengxin_watch import ChengxinWatchRadar
from radars.market_pressure import MarketPressureRadar
from radars.news_radar import NewsRadar
from radars.real_market import RealMarketPressureRadar, TaiwanCoreRadar
from storage.db import db_session
from storage.models import RadarSignal


def _normalize_results(result: RadarResult | list[RadarResult]) -> list[RadarResult]:
    if isinstance(result, list):
        return result
    return [result]


def run_all_radars() -> list[RadarSignal]:
    radars = [
        RealMarketPressureRadar(),
        TaiwanCoreRadar(),
        ChengxinWatchRadar(),
        NewsRadar(),
        MarketPressureRadar(),  # 開發測試雷達：保留對照，但決策會降低其權重。
    ]
    signals: list[RadarSignal] = []
    with db_session() as session:
        for radar in radars:
            for result in _normalize_results(radar.evaluate()):
                row = RadarSignal(
                    radar_name=result.radar_name,
                    level=result.level,
                    score=result.score,
                    summary=result.summary,
                )
                session.add(row)
                signals.append(row)
    return signals
