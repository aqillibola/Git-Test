import streamlit as st
from sqlalchemy import text
import plotly.express as px
from db import run_query

def render(start_dt, end_dt):
    query = text("""
        SELECT to_char(pay_time, 'YYYY-MM-DD HH24') AS "Кун-Соат",
        SUM(amount / 100.0) FILTER (WHERE status = 'SUCCESS') AS "Сумма"
        FROM auto_pay_items
        WHERE pay_time BETWEEN :start AND :end
        GROUP BY 1
        ORDER BY 1;
    """)
    df = run_query(query, {"start": start_dt, "end": end_dt})
    if df.empty:
        st.info("ℹ️ Танланган даврда маълумот мавжуд эмас.")
        return df

    fig = px.bar(df, x="Кун-Соат", y="Сумма", title="💰 Кун ва соат бўйича ечилган сумма",
                 labels={"Кун-Соат": "Вақт", "Сумма": "Сумма (UZS)"}, color="Сумма", color_continuous_scale="Viridis")
    fig.update_layout(xaxis_tickangle=-45, xaxis_title="Вақт (Йил-Ой-Кун Соат)", yaxis_title="Сумма", height=420, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    return df
