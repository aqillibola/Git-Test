import pandas as pd
import streamlit as st
from sqlalchemy import text

from config import ERROR_STATUS_COLORS, PASTEL_SERVICE_COLORS
from db import run_query
from components.charts import (
    card_section_start, card_section_end, chart_card_open, chart_card_close,
    service_pie, service_bar, hourly_line,
)
from components.reference import show_error_reference

def render(start_dt, end_dt):
    query = text("""
        SELECT
            api.created_at AS "Сана",
            c.owner AS "Эгаси",
            api.pinfl AS "ЖШШИР",
            api.pan AS "Карта рақами",
            c.card_service AS "Сервис",
            api.amount / 100.0 AS "Сумма",
            COALESCE(l.overdue_amount, 0) / 100.0 AS "Қарз",
            api.status AS "Статус",
            COALESCE(
                api.response_details->>'description',
                api.response_details->>'message',
                api.response_details->>'msg',
                api.response_details->>'error',
                api.response_details->>'result',
                'Номаълум'
            ) AS "Сабаб",
            COALESCE(api.response_details::text, '{}') AS "Тўлиқ JSON жавоб"
        FROM auto_pay_items api
        LEFT JOIN cards c ON api.card_id = c.uuid
        LEFT JOIN loans l ON api.loan_id = l.loan_id
        WHERE api.status IN ('ERROR', 'FAILED')
          AND api.created_at BETWEEN :start AND :end
        ORDER BY api.created_at DESC
        LIMIT 200;
    """)
    df = run_query(query, {"start": start_dt, "end": end_dt})

    if df.empty:
        st.info("ℹ️ Танланган даврда муваффақиятсиз уринишлар топилмади.")
        return df

    st.warning(f"⚠️ Жами {len(df)} та муваффақиятсиз уриниш топилди")

    df["Сана"] = pd.to_datetime(df["Сана"], errors="coerce")
    status_counts = df["Статус"].fillna("Номаълум").value_counts().reset_index()
    status_counts.columns = ["Статус", "Сони"]
    service_counts = df["Сервис"].fillna("Номаълум").value_counts().reset_index()
    service_counts.columns = ["Сервис", "Сони"]

    analysis_day = pd.Timestamp(end_dt).date()
    one_day_df = df[df["Сана"].dt.date == analysis_day].copy()

    card_section_start("📊 Хатолар визуал таҳлили", "Қайси хатолар ва қайси сервисларда муаммо кўпроқ эканини тез кўриш")
    a, b, c = st.columns(3)

    with a:
        chart_card_open()
        st.plotly_chart(service_pie(status_counts, ERROR_STATUS_COLORS, "🚦 Статуслар тақсимоти"), use_container_width=True)
        chart_card_close()

    with b:
        chart_card_open()
        st.plotly_chart(service_bar(service_counts, PASTEL_SERVICE_COLORS, "💳 Сервислар бўйича хатолар", "Карта сервиси", "Сони"), use_container_width=True)
        chart_card_close()

    with c:
        chart_card_open()
        if not one_day_df.empty:
            one_day_df["Соат"] = one_day_df["Сана"].dt.hour
            hourly = one_day_df.groupby("Соат", as_index=False).agg(
                Хатолар_сони=("Статус", "count"),
                Жами_сумма=("Сумма", "sum")
            ).sort_values("Соат")
            st.plotly_chart(
                hourly_line(hourly, "Соат", "Хатолар_сони", "Жами_сумма",
                            f"📅 Бир кунлик анализ: {analysis_day.strftime('%d.%m.%Y')}",
                            "Соат", "Хатолар сони", "#D94949", "#501C4C"),
                use_container_width=True
            )
        else:
            st.info(f"ℹ️ {analysis_day.strftime('%d.%m.%Y')} учун хатолар йўқ.")
        chart_card_close()

    card_section_end()
    show_error_reference()
    return df
