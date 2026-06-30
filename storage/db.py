from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.settings import load_settings


class Base(DeclarativeBase):
    pass


_settings = load_settings()
engine = create_engine(_settings.database.url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)


@contextmanager
def db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _ensure_news_columns() -> None:
    # Streamlit Cloud 會沿用既有 SQLite；create_all 不會自動補欄位，所以這裡做輕量 migration。
    wanted = {
        "category": "VARCHAR(120)",
        "related_symbols": "VARCHAR(300)",
        "impact_score": "FLOAT",
        "risk_score": "FLOAT",
    }
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(news_items)")).fetchall()
        existing = {row[1] for row in rows}
        for col, typ in wanted.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE news_items ADD COLUMN {col} {typ}"))


def init_db() -> None:
    from storage import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _ensure_news_columns()
