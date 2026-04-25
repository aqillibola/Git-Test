from __future__ import annotations

import pandas as pd
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.services.system_service import SystemService


def render() -> None:
    render_header("Система / Oracle", "Диагностика подключения к боевой БД")
    info = SystemService().get_oracle_info()
    df = pd.DataFrame([info]).T.reset_index()
    df.columns = ["Параметр", "Значение"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.code(
        """
Проверка вручную:
python3 - <<'PY'
import oracledb
conn = oracledb.connect(user='osago', password='uzb', dsn='192.168.11.13:1521/FREEPDB1')
print(conn.version)
print(conn.cursor().execute("select sys_context('USERENV','SERVICE_NAME') from dual").fetchone())
conn.close()
PY
        """.strip()
    )
