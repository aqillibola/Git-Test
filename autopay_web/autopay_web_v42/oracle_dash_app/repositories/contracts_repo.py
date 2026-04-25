from __future__ import annotations

from oracle_dash_app.core.config import get_settings
from oracle_dash_app.repositories.base import BaseRepository
from oracle_dash_app.sql.dynamic_queries import contracts_query


class ContractsRepository(BaseRepository):
    def list_contracts(
        self,
        search: str | None = None,
        date_field: str = "issue_date",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict]:
        settings = get_settings()
        return self.fetch_rows(
            contracts_query(),
            {
                "limit_rows": settings.page_size,
                "search": search or None,
                "date_field": date_field or "issue_date",
                "date_from": date_from or None,
                "date_to": date_to or None,
            },
        )


    def get_contract_detail(self, contract_id: int) -> dict | None:
        from oracle_dash_app.sql.dynamic_queries import contract_detail_query
        rows = self.fetch_rows(contract_detail_query(), {"contract_id": contract_id})
        return rows[0] if rows else None

    def get_contract_policies(self, contract_id: int) -> list[dict]:
        from oracle_dash_app.sql.dynamic_queries import contract_policies_query
        return self.fetch_rows(contract_policies_query(), {"contract_id": contract_id})

    def get_contract_payments(self, contract_id: int) -> list[dict]:
        from oracle_dash_app.sql.dynamic_queries import contract_payments_query
        return self.fetch_rows(contract_payments_query(), {"contract_id": contract_id})


    def get_contract_api_logs(self, contract_id: int) -> list[dict]:
        from oracle_dash_app.sql.dynamic_queries import contract_api_logs_query
        return self.fetch_rows(contract_api_logs_query(), {"contract_id": contract_id})

    def get_contract_api_log_detail(self, log_id: int) -> dict | None:
        from oracle_dash_app.sql.dynamic_queries import contract_api_log_detail_query
        rows = self.fetch_rows(contract_api_log_detail_query(), {"log_id": log_id})
        return rows[0] if rows else None
