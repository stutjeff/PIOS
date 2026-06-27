from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_sources.mock_source import MockMarketSource
from services.ingestion import save_datapoints
from services.radar_runner import run_all_radars
from storage.db import init_db


def main() -> None:
    init_db()
    count = save_datapoints(MockMarketSource().fetch())
    signals = run_all_radars()
    print(f"PIOS run complete. datapoints={count}, signals={len(signals)}")


if __name__ == "__main__":
    main()
