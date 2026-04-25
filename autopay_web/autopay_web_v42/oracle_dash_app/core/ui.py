from __future__ import annotations

from datetime import date, timedelta
import streamlit as st
from oracle_dash_app.core.config import get_settings
from oracle_dash_app.db.oracle_helpers import get_runtime_connection_info, get_active_sessions_count


DATE_FIELD_OPTIONS = {
    "Тузилган сана": "issue_date",
    "Суғурта бошланиши": "start_date",
    "Суғурта тугаши": "end_date",
    "Тўлов санаси": "payment_date",
    "Берилган сана": "issue_date",
}


def configure_page() -> None:
    settings = get_settings()
    st.set_page_config(
        page_title=settings.app_title,
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🛡️",
    )
    st.markdown(
        """
        <style>
            .block-container {padding-top: .35rem; padding-bottom: 1rem;}
            header[data-testid="stHeader"] {display:block !important; visibility:visible !important; background:transparent !important; height:auto !important; min-height:0 !important;}
            [data-testid="stToolbar"] {display:flex !important; visibility:visible !important; height:auto !important; right:.5rem !important;}
            [data-testid="collapsedControl"] {display:flex !important; visibility:visible !important; opacity:1 !important;}
            button[kind="header"] {display:flex !important; visibility:visible !important; opacity:1 !important;}
            .stAppViewContainer > .main {background: linear-gradient(180deg,#EEF2F8 0%, #F7F8FC 100%) !important;}
            .metric-card {
                border: 1px solid #d9e4f2; border-radius: 18px; padding: 16px; background: white;
                box-shadow: 0 8px 24px rgba(31,79,143,.08);
            }
            .section-card {
                border: 1px solid #d9e4f2; border-radius: 20px; padding: 18px; background: white;
                box-shadow: 0 8px 24px rgba(31,79,143,.08); margin-bottom: 12px;
            }
            .title-pill {display:none !important;}
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


def render_dashboard_sidebar() -> str:
    info = get_runtime_connection_info()
    st.sidebar.markdown("## Dashboard")
    active_sessions = get_active_sessions_count()
    if active_sessions is None:
        st.sidebar.caption("Фаол сеанслар: мавжуд эмас")
    else:
        st.sidebar.caption(f"Фаол сеанслар: {active_sessions}")
    if info.get("backend") == "oracle":
        service = info.get("service_name") or "не определён"
        st.sidebar.write(f"**Oracle хост:** {info.get('host')}:{info.get('port')}")
        st.sidebar.write(f"**Схема:** {info.get('schema')}")
        st.sidebar.write(f"**Сервис:** {service}")
    return "dashboard"


def _filters_key(page_key: str) -> str:
    return f"sidebar_filters_{page_key}"


def get_sidebar_filters(page_key: str) -> dict:
    defaults = _default_sidebar_filters(page_key)
    current = st.session_state.get(_filters_key(page_key), {})
    return {**defaults, **current}


def _default_sidebar_filters(page_key: str) -> dict:
    today = date.today()
    return {
        "search": "",
        "date_field": "issue_date",
        "date_from": today.isoformat(),
        "date_to": today.isoformat(),
    }


def render_sidebar_filters(page_key: str) -> None:
    if page_key in {"api", "system"}:
        return

    current = get_sidebar_filters(page_key)
    date_label_reverse = {v: k for k, v in DATE_FIELD_OPTIONS.items()}
    default_label = date_label_reverse.get(current.get("date_field", "issue_date"), "Тузилган сана")
    labels = list(DATE_FIELD_OPTIONS.keys())
    default_idx = labels.index(default_label) if default_label in labels else 0

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Филтр")
    with st.sidebar.form(f"sidebar_filter_form_{page_key}", clear_on_submit=False):
        search = st.text_input("Қидирув", value=current.get("search", ""), placeholder="рақам / мижоз / ҳужжат")
        date_field_label = st.selectbox("Давр", labels, index=default_idx)
        date_from = st.date_input(
            "Дан",
            value=date.fromisoformat(current.get("date_from")) if current.get("date_from") else date.today(),
            format="DD.MM.YYYY",
        )
        date_to = st.date_input(
            "Гача",
            value=date.fromisoformat(current.get("date_to")) if current.get("date_to") else date.today(),
            format="DD.MM.YYYY",
        )
        submitted = st.form_submit_button("Қидирув", use_container_width=True, type="primary")

    if submitted or _filters_key(page_key) not in st.session_state:
        st.session_state[_filters_key(page_key)] = {
            "search": (search or "").strip(),
            "date_field": DATE_FIELD_OPTIONS[date_field_label],
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
        }
