from __future__ import annotations

import pandas as pd
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.components.tables import render_dataframe
from oracle_dash_app.core.ui import get_sidebar_filters
from oracle_dash_app.services.documents_service import DocumentsService


def render() -> None:
    render_header("Документы / Печать / PDF", "APEX-аналоги: страницы 291, 294, логика печати page 730")
    filters = get_sidebar_filters("documents")
    df = pd.DataFrame(DocumentsService().list_templates(search=filters.get("search") or None))
    render_dataframe(df, key="documents_table", height=760)
    st.caption("Сейчас модуль читает виды полисов/шаблонов из INS_PTURI. Генератор PDF можно нарастить отдельно.")
