from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_sources.manager import build_default_manager
from services.news_ingestion import build_default_news_manager
from services.radar_runner import run_all_radars
from storage.db import init_db


def main() -> None:
    init_db()
    source_results = build_default_manager().fetch_all()
    news_results = build_default_news_manager().fetch_all()
    signals = run_all_radars()
    print("PIOS run completed")
    for r in source_results:
        status = "OK" if r.ok else "FAIL"
        print(f"- {r.source}: {status}, {r.count} rows, {r.error or ''}")
    print("News sources:")
    for r in news_results:
        status = "OK" if r.ok else "FAIL"
        print(f"- {r.source}: {status}, {r.count} rows, {r.error or ''}")
    print(f"Radar signals: {len(signals)}")


if __name__ == "__main__":
    main()
