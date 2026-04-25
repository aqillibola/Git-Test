from __future__ import annotations
from oracle_dash_app.repositories.clients_repo import ClientsRepository


class ClientsService:
    def __init__(self) -> None:
        self.repo = ClientsRepository()

    def list_clients(self, search: str = "") -> list[dict]:
        return self.repo.list_clients(search)
