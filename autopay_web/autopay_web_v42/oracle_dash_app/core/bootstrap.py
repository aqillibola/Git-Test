from __future__ import annotations

from pathlib import Path
from oracle_dash_app.core.config import get_settings


def bootstrap() -> None:
    settings = get_settings()
    Path("data").mkdir(exist_ok=True)
    if settings.db_backend == "sqlite":
        from oracle_dash_app.db.session import engine
        from oracle_dash_app.db.seed import create_demo_data
        create_demo_data(engine)
