from __future__ import annotations
from oracle_dash_app.repositories.documents_repo import DocumentsRepository


class DocumentsService:
    def __init__(self) -> None:
        self.repo = DocumentsRepository()

    def list_templates(self, search: str | None = None) -> list[dict]:
        return self.repo.list_templates(search=search)
