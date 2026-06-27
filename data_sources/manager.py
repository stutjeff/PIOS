from __future__ import annotations

from datetime import datetime
from typing import Iterable

from data_sources.base import DataPoint, DataSource, SourceRunResult
from services.ingestion import save_datapoints, save_source_run


class DataSourceManager:
    """PIOS unified data-source gateway.

    所有外部資料都先進這裡，再寫入標準化資料表。
    未來新增資料源，只要符合 DataSource 介面，不動主程式。
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
                result = SourceRunResult(
                    source=source.name,
                    ok=True,
                    count=count,
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

    # v0.3：先接可用市場價格源 + mock 壓力資料。下一版再加 MOPS/TPEx/Data.gov.tw。
    return DataSourceManager(
        sources=[
            YahooFinanceSource(symbols=["00662.TW", "00670L.TW", "00865B.TW", "6969.TWO"]),
            TWSESource(),
            MockMarketSource(),
        ]
    )
