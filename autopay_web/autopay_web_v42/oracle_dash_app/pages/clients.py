from __future__ import annotations

from oracle_dash_app.components.header import render_header
from oracle_dash_app.components.tables import render_df
from oracle_dash_app.core.ui import get_sidebar_filters
from oracle_dash_app.services.clients_service import ClientsService


def render() -> None:
    render_header("Клиенты", "APEX-аналоги: страницы 12, 79, 251, 286, 779")
    filters = get_sidebar_filters("clients")
    rows = ClientsService().list_clients(search=filters.get("search", ""))
    render_df(rows, key="clients_table", height=760)
