from __future__ import annotations

import streamlit as st
from oracle_dash_app.core.bootstrap import bootstrap
from oracle_dash_app.db.oracle_helpers import get_runtime_connection_info, get_active_sessions_count
from oracle_dash_app.pages.dashboard import render as render_dashboard_page


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {padding-top: 1rem; padding-bottom: 1rem;}
            .metric-card {
                border: 1px solid #d9e4f2; border-radius: 18px; padding: 16px; background: white;
                box-shadow: 0 8px 24px rgba(31,79,143,.08);
            }
            .section-card {
                border: 1px solid #d9e4f2; border-radius: 20px; padding: 18px; background: white;
                box-shadow: 0 8px 24px rgba(31,79,143,.08); margin-bottom: 12px;
            }
            .title-pill {
                display: inline-block; background: linear-gradient(90deg,#1f4f8f,#5f8fd1);
                color: white; padding: 8px 14px; border-radius: 999px; font-weight: 600;
            }
            .stTabs [data-baseweb="tab-list"] {gap: 4px;}
            .stTabs [data-baseweb="tab"] {
                height: 34px; background: linear-gradient(180deg,#f2f2f2,#dcdcdc);
                border: 1px solid #b7b7b7; border-radius: 4px 4px 0 0; padding: 0 10px;
            }
            .stTabs [aria-selected="true"] {
                background: linear-gradient(180deg,#ffffff,#e9eef8); border-bottom-color: #ffffff;
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 14px; font-weight: 600;}
            div[data-testid="stExpander"] details {border: 1px solid #cfcfcf; border-radius: 6px; background: #fafafa;}
            div[data-testid="stExpander"] summary p {font-weight: 600;}
            div[data-testid="stButton"] > button {height: 2.3rem;}
            section[data-testid="stSidebar"] .stRadio label p {font-size: 14px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_info(bottom: bool = False) -> None:
    info = get_runtime_connection_info()
    active_sessions = get_active_sessions_count()
    if not bottom:
        st.markdown('---')
        st.subheader('🛡️ Oracle бошқарув панели')
        if active_sessions is None:
            st.caption('Oracle сеанслари: мавжуд эмас')
        else:
            st.caption(f'Oracle сеанслари: {active_sessions}')
        return

    if info.get('backend') == 'oracle':
        service = info.get('service_name') or 'аниқланмаган'
        host = f"{info.get('host')}:{info.get('port')}"
        schema = info.get('schema') or '-'
        sessions = 'мавжуд эмас' if active_sessions is None else str(active_sessions)
        st.markdown(
            f"""
            <div style='margin-top:18px;padding-top:8px;border-top:1px solid rgba(255,255,255,.14);
                        font-size:10px;line-height:1.35;color:rgba(255,255,255,.58)'>
                <div>Oracle session: {sessions}</div>
                <div>Host: {host}</div>
                <div>Schema: {schema}</div>
                <div>Service: {service}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render() -> None:
    bootstrap()
    render_dashboard_page()
