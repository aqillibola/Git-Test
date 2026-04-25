from __future__ import annotations

import pandas as pd
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.services.api_service import ApiService


def render() -> None:
    render_header("API", "APEX-аналоги: страницы 700, 705, 707, 850")
    df = pd.DataFrame(ApiService().list_modules())
    st.dataframe(df, use_container_width=True, hide_index=True)
