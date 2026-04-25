import streamlit as st
from sqlalchemy import text
from db import run_query

def render(top_n):
    query = text(f"""
        WITH top_debtors AS (
            SELECT pinfl, COUNT(id) as loan_count, SUM(overdue_amount) as total_raw
            FROM loans
            WHERE is_active = true AND overdue_amount > 0
            GROUP BY pinfl
            ORDER BY total_raw DESC
            LIMIT {top_n}
        )
        SELECT
            td.pinfl AS "ЖШШИР",
            (SELECT owner FROM cards c2 WHERE c2.pinfl = td.pinfl LIMIT 1) AS "Эгаси",
            td.loan_count AS "Кредит сони",
            td.total_raw / 100.0 AS "Жами қарз"
        FROM top_debtors td
        ORDER BY td.total_raw DESC;
    """)
    df = run_query(query)
    if df.empty:
        st.info("ℹ️ Қарздорлар топилмади.")
        return df

    st.metric(f"👑 Энг катта қарздор (Топ-{top_n})", df.iloc[0]["Эгаси"])
    st.metric("💸 Суммаси", f"{df.iloc[0]['Жами қарз']:,.2f}".replace(",", " ") + " UZS")
    st.info(f"ℹ️ Жами {len(df)} та қарздор кўрсатилди.")
    return df
