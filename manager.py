from __future__ import annotations

from datetime import datetime
import json
import urllib.request

from data_sources.base import DataPoint


class TWSESource:
    """TWSE official open-data adapter.

    v0.3 先抓上市個股日均價清單作為官方源健康檢查；
    後續會加上三大法人、融資融券、指數、ETF 折溢價。
    """

    name = "twse"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL"

    def fetch(self) -> list[DataPoint]:
        req = urllib.request.Request(self.url, headers={"User-Agent": "PIOS/4.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
            rows = json.loads(resp.read().decode("utf-8"))

        now = datetime.utcnow()
        points: list[DataPoint] = []
        watch = {"00662", "00670L", "00865B", "2002"}
        for row in rows:
            code = str(row.get("Code") or row.get("證券代號") or "").strip()
            if code not in watch:
                continue
            raw_price = row.get("ClosingPrice") or row.get("收盤價") or row.get("AvgPrice") or row.get("日平均價")
            try:
                value = float(str(raw_price).replace(",", ""))
            except (TypeError, ValueError):
                value = None
            points.append(DataPoint(self.name, code, "official_avg_or_close", value, json.dumps(row, ensure_ascii=False), now))
        return points
