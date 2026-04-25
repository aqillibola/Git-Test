import pandas as pd
import streamlit as st
from sqlalchemy import text
from config import PASTEL_SERVICE_COLORS
from db import run_query
from components.charts import card_section_start, card_section_end, chart_card_open, chart_card_close, service_pie, service_bar, hourly_line

def render(start_dt, end_dt):
    query = text("""
        SELECT
            c.pinfl AS "ЖШШИР",
            c.owner AS "Эгаси",
            api.amount / 100.0 AS "Сумма",
            l.overdue_amount / 100.0 AS "Қолдиқ қарз",
            api.pay_time AS "Вақт",
            c.pan AS "Карта",
            c.card_service AS "Карта сервиси",
            l.id AS "Контракт ID"
        FROM public.auto_pay_items api
        JOIN public.cards c ON api.card_id = c.uuid
        LEFT JOIN public.loans l ON api.loan_id = l.loan_id
        WHERE api.pay_time BETWEEN :start AND :end
        ORDER BY api.pay_time DESC;
    """)
    df = run_query(query, {"start": start_dt, "end": end_dt})
    if df.empty:
        st.info("ℹ️ Маълумот мавжуд эмас.")
        return df

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Транзакция", f"{len(df):,}")
    c2.metric("👥 ЖШШИР", f"{df['ЖШШИР'].nunique():,}")
    c3.metric("💰 Жами сумма", f"{df['Сумма'].sum():,.2f}".replace(",", " ") + " UZS")
    unique_debt = df.drop_duplicates(subset=["ЖШШИР"], keep="first")["Қолдиқ қарз"].sum() if "Қолдиқ қарз" in df.columns else 0
    c4.metric("💸 Жами қолдиқ қарз", f"{unique_debt:,.2f}".replace(",", " ") + " UZS")

    df["Вақт"] = pd.to_datetime(df["Вақт"], errors="coerce")
    service_counts = df["Карта сервиси"].fillna("Номаълум").value_counts().reset_index()
    service_counts.columns = ["Сервис", "Сони"]

    if not service_counts.empty:
        analysis_day = pd.Timestamp(end_dt).date()
        one_day_df = df[df["Вақт"].dt.date == analysis_day].copy()
        card_section_start("📊 Қисқа визуал анализ", "Пул тушуми ва карта сервислари бўйича тезкор кўриниш")
        a, b, c = st.columns(3)

        with a:
            chart_card_open()
            st.plotly_chart(service_pie(service_counts, PASTEL_SERVICE_COLORS, "💳 Карта сервислари улуши"), use_container_width=True)
            chart_card_close()

        with b:
            chart_card_open()
            st.plotly_chart(service_bar(service_counts, PASTEL_SERVICE_COLORS, "📦 Карталар сони", "Карта сервиси", "Сони"), use_container_width=True)
            chart_card_close()

        with c:
            chart_card_open()
            if not one_day_df.empty:
                one_day_df["Соат"] = one_day_df["Вақт"].dt.hour
                hourly = one_day_df.groupby("Соат", as_index=False).agg(
                    Жами_сумма=("Сумма","sum"),
                    Транзакция=("Сумма","count")
                ).sort_values("Соат")
                st.plotly_chart(
                    hourly_line(hourly, "Соат", "Жами_сумма", "Транзакция",
                                f"📅 Бир кунлик анализ: {analysis_day.strftime('%d.%m.%Y')}",
                                "Соат", "Жами сумма (UZS)", "#BC5377", "#7D7986"),
                    use_container_width=True
                )
            else:
                st.info(f"ℹ️ {analysis_day.strftime('%d.%m.%Y')} учун маълумот йўқ.")
            chart_card_close()

        card_section_end()

    return df
