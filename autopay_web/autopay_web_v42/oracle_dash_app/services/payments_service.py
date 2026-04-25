from __future__ import annotations
from oracle_dash_app.repositories.payments_repo import PaymentsRepository


class PaymentsService:
    def __init__(self) -> None:
        self.repo = PaymentsRepository()

    def list_payments(
        self,
        search: str | None = None,
        date_field: str = "payment_date",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict]:
        return self.repo.list_payments(search=search, date_field=date_field, date_from=date_from, date_to=date_to)
