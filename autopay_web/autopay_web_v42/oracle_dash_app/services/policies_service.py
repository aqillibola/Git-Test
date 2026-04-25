from __future__ import annotations
from oracle_dash_app.repositories.policies_repo import PoliciesRepository


class PoliciesService:
    def __init__(self) -> None:
        self.repo = PoliciesRepository()

    def list_policies(
        self,
        search: str | None = None,
        date_field: str = "issue_date",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict]:
        return self.repo.list_policies(search=search, date_field=date_field, date_from=date_from, date_to=date_to)
