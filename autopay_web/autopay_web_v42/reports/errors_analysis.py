import streamlit as st
from sqlalchemy import text
import plotly.express as px
from db import run_query

def render(start_dt, end_dt):
    query = text("""
        SELECT response_details AS "Сабаб", COUNT(*) AS "Сони"
        FROM auto_pay_items
        WHERE status IN ('FAILED','ERROR') AND pay_time BETWEEN :start AND :end
        GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
    """)
    df = run_query(query, {"start": start_dt, "end": end_dt})
    if df.empty:
        st.info("ℹ️ Танланган даврда хатоликлар йўқ.")
        return df

    fig = px.pie(df, names="Сабаб", values="Сони")
    fig.update_layout(height=420, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    return df
