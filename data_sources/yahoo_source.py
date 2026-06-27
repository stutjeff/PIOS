from __future__ import annotations

from datetime import datetime
import json
import urllib.parse
import urllib.request

from data_sources.base import DataPoint


class YahooFinanceSource:
    """Yahoo Finance adapter with per-symbol isolation.

    v0.4 原則：某個 symbol 404 / 無資料，不讓整個 Yahoo 資料源失敗。
    成功的先寫入，失敗的寫成 health/error datapoint 供 UI 顯示。
    """

    name = "yahoo_finance"

    def __init__(self, symbols: list[str], timeout: int = 10):
        self.symbols = symbols
        self.timeout = timeout

    def fetch(self) -> list[DataPoint]:
        points: list[DataPoint] = []
        now = datetime.utcnow()
        failures: list[str] = []

        for symbol in self.symbols:
            try:
                points.extend(self._fetch_symbol(symbol, now))
            except Exception as exc:  # noqa: BLE001 - symbol isolation is intentional
                failures.append(f"{symbol}: {exc}")
                points.append(
                    DataPoint(
                        self.name,
                        symbol,
                        "source_symbol_error",
                        None,
                        str(exc)[:500],
                        now,
                    )
                )

        if failures:
            points.append(
                DataPoint(
                    self.name,
                    "_SOURCE_HEALTH",
                    "failed_symbols",
                    float(len(failures)),
                    " | ".join(failures)[:1000],
                    now,
                )
            )
        return points

    def _fetch_symbol(self, symbol: str, now: datetime) -> list[DataPoint]:
        encoded = urllib.parse.quote(symbol, safe="")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=5d&interval=1d"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 PIOS/4.0",
                "Accept": "application/json,text/plain,*/*",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))

        result = payload.get("chart", {}).get("result") or []
        if not result:
            raise ValueError("empty chart result")

        meta = result[0].get("meta", {})
        quote = (result[0].get("indicators", {}).get("quote") or [{}])[0]
        closes = [v for v in quote.get("close", []) if v is not None]
        volumes = [v for v in quote.get("volume", []) if v is not None]

        price = meta.get("regularMarketPrice") or (closes[-1] if closes else None)
        volume = volumes[-1] if volumes else None
        currency = meta.get("currency")
        out = [DataPoint(self.name, symbol, "close", float(price) if price is not None else None, currency, now)]
        if volume is not None:
            out.append(DataPoint(self.name, symbol, "volume", float(volume), None, now))
        return out
