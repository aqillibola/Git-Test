from __future__ import annotations

import pandas as pd
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.components.tables import render_dataframe
from oracle_dash_app.core.ui import get_sidebar_filters
from oracle_dash_app.services.policies_service import PoliciesService


def render() -> None:
    render_header("Полисы", "APEX-аналоги: страницы 11, 160, 241, 700, 705, 707, 724, 730")
    filters = get_sidebar_filters("policies")
    df = pd.DataFrame(PoliciesService().list_policies(
        search=filters.get("search") or None,
        date_field="issue_date",
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
    ))
    render_dataframe(df, key="policies_table", height=760)

    tab1, tab2 = st.tabs(["Реестр", "Операции"])
    with tab1:
        st.info("Данные берутся из INS_POLIS + INS_ANKETA.")
    with tab2:
        st.write("Операции: выпуск, аннулирование, перевыпуск, отправка в фонд, работа со статусами.")
