from __future__ import annotations

from sqlalchemy.orm import sessionmaker
from oracle_dash_app.db.oracle_helpers import get_engine

engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session():
    return SessionLocal()
