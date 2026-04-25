from __future__ import annotations

from oracle_dash_app.core.config import get_settings
from oracle_dash_app.repositories.base import BaseRepository
from oracle_dash_app.sql.queries import API_MODULES


class ApiRepository(BaseRepository):
    def list_modules(self) -> list[dict]:
        settings = get_settings()
        return self.fetch_rows(API_MODULES, {"limit_rows": settings.page_size})
