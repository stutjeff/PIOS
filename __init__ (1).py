from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Any


@dataclass(frozen=True)
class DataPoint:
    source: str
    symbol: str
    metric: str
    value: float | None
    raw_text: str | None = None
    captured_at: datetime | None = None


@dataclass
class SourceRunResult:
    source: str
    ok: bool
    count: int = 0
    error: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None


class DataSource(Protocol):
    name: str

    def fetch(self) -> list[DataPoint]:
        """Return normalized datapoints. Source errors should be handled by manager."""
