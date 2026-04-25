from __future__ import annotations
from oracle_dash_app.repositories.api_repo import ApiRepository


class ApiService:
    def __init__(self) -> None:
        self.repo = ApiRepository()

    def list_modules(self) -> list[dict]:
        return self.repo.list_modules()
