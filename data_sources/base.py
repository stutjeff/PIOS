from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class DataPoint:
    source: str
    symbol: str
    metric: str
    value: float | None
    raw_text: str | None = None
    captured_at: datetime | None = None


class DataSource(Protocol):
    name: str

    def fetch(self) -> list[DataPoint]:
        """Return normalized datapoints. Never raise for a single bad row."""
