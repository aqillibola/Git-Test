from __future__ import annotations

from oracle_dash_app.core.config import get_settings
from oracle_dash_app.repositories.base import BaseRepository
from oracle_dash_app.sql.dynamic_queries import payments_query


class PaymentsRepository(BaseRepository):
    def list_payments(
        self,
        search: str | None = None,
        date_field: str = "payment_date",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict]:
        settings = get_settings()
        return self.fetch_rows(
            payments_query(),
            {
                "limit_rows": settings.page_size,
                "search": search or None,
                "date_field": date_field or "payment_date",
                "date_from": date_from or None,
                "date_to": date_to or None,
            },
        )
