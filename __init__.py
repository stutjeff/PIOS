from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config" / "settings.yml"


class AppSettings(BaseModel):
    name: str = "PIOS 4.0 Enterprise"
    timezone: str = "Asia/Taipei"
    base_currency: str = "TWD"


class DatabaseSettings(BaseModel):
    url: str = "sqlite:///pios4.db"


class PiosSettings(BaseModel):
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    portfolio: dict[str, Any] = Field(default_factory=dict)
    radars: dict[str, Any] = Field(default_factory=dict)
    watchlist: dict[str, Any] = Field(default_factory=dict)


def load_settings(path: Path = CONFIG_PATH) -> PiosSettings:
    load_dotenv(ROOT_DIR / ".env")
    raw: dict[str, Any] = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    settings = PiosSettings(**raw)
    env_db = os.getenv("PIOS_DB_URL")
    if env_db:
        settings.database.url = env_db
    return settings
