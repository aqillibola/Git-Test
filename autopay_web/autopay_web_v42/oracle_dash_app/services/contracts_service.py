from __future__ import annotations
from oracle_dash_app.repositories.contracts_repo import ContractsRepository


class ContractsService:
    def __init__(self) -> None:
        self.repo = ContractsRepository()

    def list_contracts(
        self,
        search: str | None = None,
        date_field: str = "issue_date",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict]:
        return self.repo.list_contracts(
            search=search,
            date_field=date_field,
            date_from=date_from,
            date_to=date_to,
        )


    def get_contract_detail(self, contract_id: int) -> dict | None:
        return self.repo.get_contract_detail(contract_id)

    def get_contract_policies(self, contract_id: int) -> list[dict]:
        return self.repo.get_contract_policies(contract_id)

    def get_contract_payments(self, contract_id: int) -> list[dict]:
        return self.repo.get_contract_payments(contract_id)


    def get_contract_api_logs(self, contract_id: int) -> list[dict]:
        return self.repo.get_contract_api_logs(contract_id)

    def get_contract_api_log_detail(self, log_id: int) -> dict | None:
        return self.repo.get_contract_api_log_detail(log_id)
