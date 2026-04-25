from __future__ import annotations

from oracle_dash_app.core.config import get_settings
from oracle_dash_app.repositories.base import BaseRepository
from oracle_dash_app.sql.dynamic_queries import documents_query


class DocumentsRepository(BaseRepository):
    def list_templates(self, search: str | None = None) -> list[dict]:
        settings = get_settings()
        return self.fetch_rows(documents_query(), {"limit_rows": settings.page_size, "search": search or None})
