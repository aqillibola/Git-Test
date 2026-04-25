import streamlit as st
from sqlalchemy import text
import plotly.express as px
from db import run_query

def render(start_dt, end_dt):
    query = text("""
        SELECT to_char(pay_time, 'YYYY-MM-DD') AS "Кун",
        COUNT(*) FILTER (WHERE status = 'SUCCESS') AS "OK",
        COUNT(*) FILTER (WHERE status IN ('FAILED','ERROR')) AS "FAIL"
        FROM auto_pay_items
        WHERE pay_time BETWEEN :start AND :end
        GROUP BY 1
        ORDER BY 1;
    """)
    df = run_query(query, {"start": start_dt, "end": end_dt})
    if df.empty:
        st.info("ℹ️ Танланган даврда статистика мавжуд эмас.")
        return df

    fig = px.line(df, x="Кун", y=["OK", "FAIL"], markers=True)
    fig.update_layout(height=420, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    return df
