import streamlit as st
from sqlalchemy import text
from db import run_query

def render(search_input):
    if not search_input:
        st.info("ℹ️ ЖШШИР киритинг.")
        return None

    query = text("""
        SELECT
            COALESCE(c.owner, 'Номаълум') AS "Эгаси",
            api.pay_time AS "Вақт",
            api.amount / 100.0 AS "Сумма",
            api.status AS "Ҳолат",
            api.pan AS "Карта",
            c.card_service AS "Карта сервиси",
            l.loan_id AS "Шартнома ID",
            COALESCE(l.overdue_amount, 0) / 100.0 AS "Қолган қарз"
        FROM public.auto_pay_items api
        LEFT JOIN public.cards c
            ON api.card_id = c.uuid
        LEFT JOIN public.loans l
            ON api.loan_id = l.loan_id
        WHERE api.pinfl = :search_id
        ORDER BY api.pay_time DESC
        LIMIT 100;
    """)
    df = run_query(query, {"search_id": search_input})

    if df.empty:
        st.warning(f"⚠️ ЖШШИР '{search_input}' бўйича маълумот йўқ")
        return df

    st.success(f"✅ {len(df)} та топилди")
    return df
