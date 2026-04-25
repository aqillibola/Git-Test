import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from config import DB_URL

pd.set_option("styler.render.max_elements", 10_000_000)

@st.cache_resource
def get_engine():
    return create_engine(
        DB_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"connect_timeout": 10},
    )

engine = get_engine()

def run_query(sql_query, params=None):
    try:
        with engine.connect() as conn:
            if isinstance(sql_query, str):
                sql_query = text(sql_query)
            return pd.read_sql(sql_query, conn, params=params)
    except Exception as e:
        st.error(f"❌ SQL хатолик: {e}")
        return pd.DataFrame()
