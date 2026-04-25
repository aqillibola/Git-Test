from __future__ import annotations

import pandas as pd
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.components.tables import render_dataframe
from oracle_dash_app.core.ui import get_sidebar_filters
from oracle_dash_app.services.contracts_service import ContractsService
from oracle_dash_app.services.payments_service import PaymentsService
from oracle_dash_app.services.policies_service import PoliciesService


def render() -> None:
    render_header("Отчёты", "Срезы по договорам, платежам и полисам из Oracle")
    filters = get_sidebar_filters("reports")
    tab1, tab2, tab3 = st.tabs(["Договоры", "Платежи", "Полисы"])

    with tab1:
        render_dataframe(pd.DataFrame(ContractsService().list_contracts(
            search=filters.get("search") or None,
            date_field=filters.get("date_field", "issue_date"),
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
        )), key="reports_contracts", height=760)
    with tab2:
        render_dataframe(pd.DataFrame(PaymentsService().list_payments(
            search=filters.get("search") or None,
            date_field="payment_date",
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
        )), key="reports_payments", height=760)
    with tab3:
        render_dataframe(pd.DataFrame(PoliciesService().list_policies(
            search=filters.get("search") or None,
            date_field="issue_date",
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
        )), key="reports_policies", height=760)
