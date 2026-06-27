from __future__ import annotations

from datetime import datetime
from typing import Iterable

from data_sources.base import DataPoint, DataSource, SourceRunResult
from services.ingestion import save_datapoints, save_source_run


class DataSourceManager:
    """PIOS unified data-source gateway.

    所有外部資料都先進這裡，再寫入標準化資料表。
    新增資料源只要符合 DataSource 介面，不動主程式。
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
                result = SourceRunResult(
                    source=source.name,
                    ok=len(symbol_errors) == 0,
                    count=count,
                    error=(f"{len(symbol_errors)} symbol errors; partial data saved" if symbol_errors else None),
                    started_at=started,
                    finished_at=datetime.utcnow(),
                )
            except Exception as exc:  # noqa: BLE001 - source isolation is intentional
                result = SourceRunResult(
                    source=source.name,
                    ok=False,
                    count=0,
                    error=str(exc),
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
            YahooFinanceSource(symbols=["QQQ", "00670L.TW", "2002.TW", "6969.TWO"]),
            TWSESource(),
            MockMarketSource(),  # v0.4 保留，只供雷達總分驗證；UI 會標成測試資料。
        ]
    )
