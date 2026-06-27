from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apscheduler.schedulers.blocking import BlockingScheduler

from storage.db import init_db
from data_sources.mock_source import MockMarketSource
from services.ingestion import save_datapoints
from services.radar_runner import run_all_radars


def pios_cycle() -> None:
    init_db()
    save_datapoints(MockMarketSource().fetch())
    run_all_radars()


def main() -> None:
    scheduler = BlockingScheduler(timezone="Asia/Taipei")
    scheduler.add_job(pios_cycle, "cron", hour="8,22", minute=0)
    scheduler.start()


if __name__ == "__main__":
    main()
