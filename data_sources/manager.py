from __future__ import annotations

from datetime import datetime
from typing import Iterable

from data_sources.base import DataPoint, DataSource, SourceRunResult
from services.ingestion import save_datapoints, save_source_run


class DataSourceManager:
    """PIOS unified data-source gateway.

    v0.5 原則：資料源可以部分失敗，但不能拖垮整個系統。
    """

    def __init__(self, sources: Iterable[DataSource]):
        self.sources = list(sources)

    def fetch_all(self) -> list[SourceRunResult]:
        results: list[SourceRunResult] = []
        for source in self.sources:
            started = datetime.utcnow()
            try:
                points = source.fetch()
                count = save_datapoints(points)
                symbol_errors = [p for p in points if p.metric == "source_symbol_error"]
                source_errors = [p for p in points if p.metric == "source_error"]
                errors = symbol_errors + source_errors
                result = SourceRunResult(
                    source=source.name,
                    ok=len(errors) == 0,
                    count=count,
                    error=(f"{len(errors)} errors; partial data saved" if errors else None),
                    started_at=started,
                    finished_at=datetime.utcnow(),
                )
            except Exception as exc:  # noqa: BLE001 - source isolation is intentional
                result = SourceRunResult(
                    source=source.name,
                    ok=False,
                    count=0,
                    error=str(exc)[:1000],
                    started_at=started,
                    finished_at=datetime.utcnow(),
                )
            save_source_run(result)
            results.append(result)
        return results


def build_default_manager() -> DataSourceManager:
    from data_sources.mock_source import MockMarketSource
    from data_sources.twse_source import TWSESource
    from data_sources.yahoo_source import YahooFinanceSource

    return DataSourceManager(
        sources=[
            YahooFinanceSource(
                symbols=[
                    "QQQ",       # Nasdaq 100 ETF：核心風險資產代理
                    "^VIX",      # 波動率壓力
                    "TLT",       # 長天期美債壓力代理
                    "00670L.TW",  # 台股正二
                    "00662.TW",   # 電力基建 ETF
                    "00865B.TW",  # 短天期美債 ETF
                    "2002.TW",    # 中鋼
                    "6969.TWO",   # 成信：可能 Yahoo 無資料，允許 partial
                ]
            ),
            TWSESource(),
            MockMarketSource(),  # 僅保留為開發測試資料，正式總分不再依賴它。
        ]
    )
