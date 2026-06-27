from __future__ import annotations

from data_sources.base import DataPoint, DataSource


class TWSESource(DataSource):
    """台灣證交所資料源預留接口。

    v0.2 先保留乾淨接口，下一版開始接每日收盤、法人、融資融券等資料。
    """

    name = "twse"

    def fetch(self) -> list[DataPoint]:
        return []
