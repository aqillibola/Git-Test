from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.components.tables import render_dataframe
from oracle_dash_app.core.ui import get_sidebar_filters
from oracle_dash_app.services.payments_service import PaymentsService


def render() -> None:
    render_header("Оплата", "APEX-аналог: страница 29")
    filters = get_sidebar_filters("payments")
    df = pd.DataFrame(PaymentsService().list_payments(
        search=filters.get("search") or None,
        date_field="payment_date",
        date_from=filters.get("date_from"),
        date_to=filters.get("date_to"),
    ))
    render_dataframe(df, key="payments_table", height=760)
    if not df.empty and "document_no" in df.columns and "amount" in df.columns:
        fig = px.bar(df.head(30), x="document_no", y="amount", title="Суммы платежей")
        st.plotly_chart(fig, use_container_width=True)
