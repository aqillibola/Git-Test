from __future__ import annotations

from oracle_dash_app.core.config import get_settings
from oracle_dash_app.repositories.base import BaseRepository
from oracle_dash_app.sql.dynamic_queries import clients_query


class ClientsRepository(BaseRepository):
    def list_clients(self, search: str = "") -> list[dict]:
        settings = get_settings()
        return self.fetch_rows(clients_query(), {"search": search, "limit_rows": settings.page_size})
