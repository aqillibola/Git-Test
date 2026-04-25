import streamlit as st
from sqlalchemy import text

from db import run_query
from components.charts import (
    card_section_start,
    card_section_end,
    chart_card_open,
    chart_card_close,
    service_pie,
    service_bar,
)


def render():
    query = text("""
        SELECT
            api.id AS "Транзакция ID",
            api.pay_time AS "Тўлов вақти",
            c.owner AS "Мижоз",
            c.pinfl AS "ЖШШИР",
            c.pan AS "Карта рақами",
            c.card_service AS "Сервис",
            api.amount / 100.0 AS "Ечилган сумма (сўм)",
            l.loan_id AS "Контракт ID",
            l.overdue_amount / 100.0 AS "Қолган қарз (сўм)"
        FROM public.auto_pay_items api
        JOIN public.cards c ON api.card_id = c.uuid
        LEFT JOIN public.loans l ON api.loan_id = l.loan_id
        WHERE api.status = 'SUCCESS'
        ORDER BY api.pay_time DESC;
    """)
    df = run_query(query)

    if df.empty:
        st.info("ℹ️ Маълумот топилмади.")
        return df

    total_tx = len(df)
    total_sum = df["Ечилган сумма (сўм)"].fillna(0).sum()
    total_debt = df["Қолган қарз (сўм)"].fillna(0).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("📄 Жами муваффақиятли транзакция", f"{total_tx:,}")
    c2.metric("💳 Жами ечилган сумма", f"{total_sum:,.2f}".replace(",", " ") + " UZS")
    c3.metric("💸 Жами қолган қарз", f"{total_debt:,.2f}".replace(",", " ") + " UZS")

    service_counts = (
        df["Сервис"]
        .fillna("Номаълум")
        .value_counts()
        .reset_index()
    )
    service_counts.columns = ["Сервис", "Сони"]

    amount_by_service = (
        df.groupby(df["Сервис"].fillna("Номаълум"), dropna=False)["Ечилган сумма (сўм)"]
        .sum()
        .reset_index()
    )
    amount_by_service.columns = ["Сервис", "Ечилган сумма"]

    chart_colors = {
        "HUMO": "#BC5377",
        "UZCARD": "#7D7986",
        "Номаълум": "#C9EEE1",
    }

    card_section_start("📊 Қарздорлар (барча) визуал таҳлили", "SUCCESS транзакциялар бўйича ҳисобланган кўриниш")
    a, b = st.columns(2)

    with a:
        chart_card_open()
        st.plotly_chart(
            service_pie(service_counts, chart_colors, "💳 Сервислар улуши"),
            use_container_width=True,
        )
        chart_card_close()

    with b:
        chart_card_open()
        st.plotly_chart(
            service_bar(
                amount_by_service,
                chart_colors,
                "💰 Сервис бўйича ечилган сумма",
                "Карта сервиси",
                "Ечилган сумма",
            ),
            use_container_width=True,
        )
        chart_card_close()

    card_section_end()
    return df
