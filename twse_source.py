from __future__ import annotations

from datetime import datetime
from random import uniform

from data_sources.base import DataPoint


class MockMarketSource:
    name = "mock_market"

    def fetch(self) -> list[DataPoint]:
        now = datetime.utcnow()
        return [
            DataPoint(self.name, "TW_MARKET", "momentum_score", round(uniform(20, 80), 2), captured_at=now),
            DataPoint(self.name, "TW_MARKET", "margin_pressure", round(uniform(10, 90), 2), captured_at=now),
            DataPoint(self.name, "US_MARKET", "credit_spread_pressure", round(uniform(15, 85), 2), captured_at=now),
        ]
