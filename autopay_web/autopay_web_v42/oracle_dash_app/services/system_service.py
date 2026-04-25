from __future__ import annotations
from oracle_dash_app.repositories.system_repo import SystemRepository


class SystemService:
    def __init__(self) -> None:
        self.repo = SystemRepository()

    def get_oracle_info(self) -> dict:
        return self.repo.get_oracle_info()
