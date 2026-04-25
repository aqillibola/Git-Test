import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from config import APP_TITLE, APP_VERSION, DEFAULT_END_DATE, DEFAULT_START_DATE, BASE_MENU, ADMIN_MENU
from styles import inject_css
from auth import require_auth, login_form, logout, current_user, get_allowed_menu_for_role, touch_session, get_active_session_users
from components.header import render_header
from components.tables import display_dataframe
from reports import incoming_money, failed_cards, top_debtors, all_debtors, good_hours, daily_stats, rabbitqm, api_amount_java_monitor, pinfl_search, admin_panel
from oracle_dashboard_bridge import render as render_oracle_dashboard
from oracle_dashboard_bridge import inject_styles as inject_oracle_dashboard_styles, render_sidebar_info as render_oracle_sidebar_info

st.set_page_config(page_title=APP_TITLE, page_icon="🚜", layout="wide", initial_sidebar_state="expanded")
inject_css()

REFRESH_OPTIONS = {
    "Ўчирилган": 0,
    "1с": 1,
    "10с": 10,
    "1м": 60,
    "5м": 300,
    "10м": 600,
}
AUTO_REFRESH_PAGES = ["📊 Dashboard", "💸 Келиб тушган пул ва қолдиқ"]
FULL_MENU = BASE_MENU + ADMIN_MENU


def enable_auto_refresh(seconds: int):
    if seconds and seconds > 0:
        components.html(
            f"""
            <script>
                setTimeout(function() {{
                    window.parent.location.reload();
                }}, {seconds * 1000});
            </script>
            """,
            height=0,
        )


if not require_auth():
    st.markdown('<div class="login-spacer-top"></div>', unsafe_allow_html=True)
    left, center, right = st.columns([1.5, 1, 1.5])
    with center:
        st.markdown('<div class="login-shell"><div class="login-box">', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="login-brand">
                <div class="login-brand-title">🚜 {APP_TITLE}</div>
                <div class="login-brand-sub">Авторизация орқали кириш</div>
            </div>
            <div class="login-divider"></div>
            <div class="login-card-title">🔐 Тизимга кириш</div>
            <div class="login-card-sub">Login ва пароль орқали киринг</div>
        """, unsafe_allow_html=True)
        login_form()
        st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

user = current_user()
touch_session()
active_session_users = get_active_session_users()
menu = get_allowed_menu_for_role(user.get("role", "viewer"), FULL_MENU)
if not menu:
    st.error("Сизга бирорта ҳам меню рухсат берилмаган. Админга мурожаат қилинг.")
    st.stop()

with st.sidebar:
    st.header("📊 Бошқарув")
    st.markdown("---")
    st.subheader("👥 Тизим ҳолати")
    st.caption(f"👤 Фойдаланувчи: `{user.get('full_name', 'Unknown')}`")
    st.caption(f"🛡️ Роль: `{user.get('role', 'viewer')}`")
    st.metric("Фаол сессия", str(len(active_session_users)))
    if active_session_users:
        st.caption("Сессиядаги фойдаланувчилар:")
        for sess_user in active_session_users:
            st.caption(f"• {sess_user.get('full_name', sess_user.get('username', 'Unknown'))}")
    st.button("🚪 Чиқиш", on_click=logout, use_container_width=True)
    st.markdown("---")
    default_choice = "💸 Келиб тушган пул ва қолдиқ" if "💸 Келиб тушган пул ва қолдиқ" in menu else menu[0]
    if st.session_state.get("selected_report") not in menu:
        st.session_state["selected_report"] = default_choice
    choice = st.selectbox(
        "Ҳисоботни танланг",
        menu,
        index=menu.index(st.session_state["selected_report"]),
        key="selected_report",
    )
    top_n = 10
    if choice == "🏆 Топ Қарздорлар":
        st.markdown("---")
        st.subheader("⚙️ Танламалар")
        top_n = st.selectbox("Не та қарздорни кўрсатиш?", [10, 20, 50, 100], index=0)
    st.subheader("📅 Саналар")
    if "start_date" not in st.session_state:
        st.session_state.start_date = DEFAULT_START_DATE
    if "end_date" not in st.session_state:
        st.session_state.end_date = DEFAULT_END_DATE
    st.session_state.start_date = st.date_input("Бошланиш санаси", value=st.session_state.start_date)
    st.session_state.end_date = st.date_input("Тугаш санаси", value=st.session_state.end_date)
    search_btn = st.button("🔍 Қидирувни бошлаш", type="primary", use_container_width=True)

    auto_refresh_enabled = False
    refresh_seconds = 0
    if choice in AUTO_REFRESH_PAGES:
        st.session_state.setdefault(f"auto_refresh_enabled_{choice}", False)
        label = "⏸️ Автоянгилашни ўчириш" if st.session_state[f"auto_refresh_enabled_{choice}"] else "🔄 Автоянгилашни ёқиш"
        if st.button(label, use_container_width=True):
            st.session_state[f"auto_refresh_enabled_{choice}"] = not st.session_state[f"auto_refresh_enabled_{choice}"]
            st.rerun()
        interval_label = st.radio(
            "Автоянгилаш оралиғи",
            list(REFRESH_OPTIONS.keys()),
            horizontal=True,
            index=1 if choice == "📊 Dashboard" else 2,
            key=f"refresh_interval_{choice}",
        )
        auto_refresh_enabled = st.session_state[f"auto_refresh_enabled_{choice}"]
        refresh_seconds = REFRESH_OPTIONS[interval_label] if auto_refresh_enabled else 0
        if auto_refresh_enabled:
            st.caption(f"Автоянгилаш ёқилган: ҳар {interval_label} да")

    table_height = st.slider("📏 Жадвал баландлиги", 400, 2500, 800)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    render_oracle_sidebar_info(bottom=True)

if choice == "📊 Dashboard":
    if refresh_seconds:
        enable_auto_refresh(refresh_seconds)
    inject_oracle_dashboard_styles()
    try:
        render_oracle_dashboard()
    except Exception as e:
        st.error(f"❌ Dashboard хатолик: {e}")
    st.stop()

if choice != "⚙️ Админ панель":
    st.info(
        f"📅 Танланган давр: **{st.session_state.start_date.strftime('%d.%m.%Y')}** дан "
        f"**{st.session_state.end_date.strftime('%d.%m.%Y')}** гача"
    )

search_input = None
if choice == "🔎 ЖШШИР бўйича қидирув":
    st.subheader("🔎 ЖШШИР киритиш")
    raw = st.text_input("ЖШШИР", placeholder="123456789012")
    if raw:
        search_input = raw.strip()

start_dt = pd.Timestamp(st.session_state.start_date)
end_dt = pd.Timestamp(st.session_state.end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
df = pd.DataFrame()

if choice == "⚙️ Админ панель":
    admin_panel.render()
    st.stop()

should_run = search_btn or (choice == "💸 Келиб тушган пул ва қолдиқ" and refresh_seconds > 0)

if should_run:
    if refresh_seconds:
        enable_auto_refresh(refresh_seconds)
    start_time = time.time()
    status_box = st.empty()
    progress_box = st.empty()
    time_box = st.empty()

    status_box.info("🔄 Маълумотлар юкланмоқда...")
    progress = progress_box.progress(0)
    time_box.caption("⏱️ Бошланди...")

    try:
        progress.progress(10)
        time_box.caption(f"⏱️ Ўтган вақт: {time.time() - start_time:.1f} сек")

        if choice == "💸 Келиб тушган пул ва қолдиқ":
            progress.progress(30)
            df = incoming_money.render(start_dt, end_dt)
        elif choice == "🚫 Ечилмайдиган карталар (Имтиёзли)":
            progress.progress(30)
            df = failed_cards.render(start_dt, end_dt)
        elif choice == "🏆 Топ Қарздорлар":
            progress.progress(30)
            df = top_debtors.render(top_n)
        elif choice == "📋 Қарздорлар (Барча)":
            progress.progress(30)
            df = all_debtors.render()
        elif choice == "🕐 Пул ечишга қулай соатлар":
            progress.progress(30)
            df = good_hours.render(start_dt, end_dt)
        elif choice == "📈 Кунлик статистика (%)":
            progress.progress(30)
            df = daily_stats.render(start_dt, end_dt)
        elif choice == "🐇 RabbitQM":
            progress.progress(30)
            df = rabbitqm.render(start_dt, end_dt)
        elif choice == "☕ AutoPay Amount Java API мониторинг":
            progress.progress(30)
            df = api_amount_java_monitor.render(start_dt, end_dt)
        elif choice == "🔎 ЖШШИР бўйича қидирув":
            progress.progress(30)
            result = pinfl_search.render(search_input)
            if result is not None:
                df = result

        progress.progress(70)
        time_box.caption(f"⏱️ Ўтган вақт: {time.time() - start_time:.1f} сек")

        if isinstance(df, pd.DataFrame) and not df.empty and choice == "🔎 ЖШШИР бўйича қидирув":
            display_dataframe(df, height=table_height)

        progress.progress(100)
        elapsed = time.time() - start_time
        status_box.success(f"✅ Тайёр! Бажарилиш вақти: {elapsed:.2f} сек")
        time_box.caption(f"⏱️ Жами вақт: {elapsed:.2f} сек")

    except Exception as e:
        elapsed = time.time() - start_time
        status_box.error(f"❌ Хатолик: {e}")
        time_box.caption(f"⏱️ Хатогача ўтган вақт: {elapsed:.2f} сек")
else:
    if choice == "💸 Келиб тушган пул ва қолдиқ":
        st.info("ℹ️ Автоянгилашни ёқсангиз ёки қидирув тугмасини боссангиз маълумот чиқади.")
    else:
        st.info("ℹ️ Саналарни танлаб, «🔍 Қидирувни бошлаш» тугмасини босинг.")

if (
    isinstance(df, pd.DataFrame)
    and not df.empty
    and choice != "🔎 ЖШШИР бўйича қидирув"
    and choice not in ["🕐 Пул ечишга қулай соатлар", "📈 Кунлик статистика (%)", "📡 AutoPay Ping мониторинг", "🐇 RabbitQM", "☕ AutoPay Amount Java API мониторинг"]
):
    display_dataframe(df, height=table_height)

st.markdown("---")
st.caption(
    f"<div style='text-align: center; color:#6B728A;'>🚜 {APP_VERSION} — Full Animated Admin UI</div>",
    unsafe_allow_html=True,
)
