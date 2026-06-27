from __future__ import annotations

from data_sources.base import DataPoint, DataSource


class MOPSSource(DataSource):
    """公開資訊觀測站資料源預留接口。"""

    name = "mops"

    def fetch(self) -> list[DataPoint]:
        return []
