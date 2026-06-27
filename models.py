from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RadarResult:
    radar_name: str
    level: str
    score: float
    summary: str


class Radar:
    name: str = "base"

    def evaluate(self) -> RadarResult:
        raise NotImplementedError
