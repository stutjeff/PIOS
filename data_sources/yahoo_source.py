from __future__ import annotations

from datetime import datetime
import json
import urllib.request

from data_sources.base import DataPoint


class YahooFinanceSource:
    """Yahoo Finance chart endpoint adapter.

    用途：先穩定取得核心 ETF / 個股的最新價格。若失敗，DataSourceManager 會隔離錯誤，
    不會拖垮整個 PIOS。
    """

    name = "yahoo_finance"

    def __init__(self, symbols: list[str], timeout: int = 10):
        self.symbols = symbols
        self.timeout = timeout

    def fetch(self) -> list[DataPoint]:
        points: list[DataPoint] = []
        now = datetime.utcnow()
        for symbol in self.symbols:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
            req = urllib.request.Request(url, headers={"User-Agent": "PIOS/4.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
                payload = json.loads(resp.read().decode("utf-8"))

            result = payload.get("chart", {}).get("result") or []
            if not result:
                continue
            meta = result[0].get("meta", {})
            quote = (result[0].get("indicators", {}).get("quote") or [{}])[0]
            closes = [v for v in quote.get("close", []) if v is not None]
            volumes = [v for v in quote.get("volume", []) if v is not None]

            price = meta.get("regularMarketPrice") or (closes[-1] if closes else None)
            volume = volumes[-1] if volumes else None
            currency = meta.get("currency")

            points.append(DataPoint(self.name, symbol, "close", float(price) if price is not None else None, currency, now))
            if volume is not None:
                points.append(DataPoint(self.name, symbol, "volume", float(volume), None, now))
        return points
