from __future__ import annotations

import math
import time
from datetime import date, datetime
from urllib.parse import urlencode, urlparse
import pandas as pd
import plotly.express as px
import streamlit as st
from oracle_dash_app.components.header import render_header
from oracle_dash_app.components.tables import render_dataframe
from oracle_dash_app.core.ui import get_sidebar_filters
from oracle_dash_app.services.contracts_service import ContractsService


LABEL_MAP = {
    "contract_id": "ID договора",
    "contract_no": "№ договора",
    "client_id": "Клиент ID",
    "client_name": "Страхователь",
    "insurance_type_id": "Вид страхования",
    "insurance_type_name": "Вид страхования",
    "insurance_object": "Объект страхования",
    "insurance_class": "Класс страхования",
    "product_code": "Код продукта",
    "division_name": "Подразделение",
    "currency_name": "Валюта",
    "amount_paid": "Поступившая сумма",
    "amount_paid_display": "Поступившая сумма",
    "premium_display": "Премия",
    "liability_display": "Ответственность",
    "issue_date": "Дата заключения",
    "start_date": "Начало страхования",
    "end_date": "Конец страхования",
    "premium": "Премия",
    "liability": "Ответственность",
    "ins_id": "ID записи",
    "ins_div": "Подразделение ID",
    "ins_num": "Номер договора",
    "ins_date": "Дата оформления",
    "ins_type": "Тип страхования",
    "ins_datef": "Начало действия",
    "ins_datet": "Конец действия",
    "ins_prem": "Премия",
    "ins_otv": "Ответственность",
    "owner": "Страхователь ID",
    "status": "Статус",
    "log_id": "LOG_ID",
    "log_date": "Дата",
    "api_name": "API",
    "status_code": "HTTP",
    "timespent": "Время",
    "usr": "Пользователь",
    "log_div": "Подразделение",
    "anketa_id": "ANKETA_ID",
    "polis_id": "POLIS_ID",
    "reason_phrase": "Причина",
    "error_code": "Код ошибки",
    "error_text": "Текст ошибки",
    "error_info": "Подробности ошибки",
    "http_version": "HTTP version",
    "created_by": "Пользователь / Создал",
}


DATE_LABELS = {
    "issue_date", "start_date", "end_date", "ins_date", "ins_datef", "ins_datet", "log_date", "payment_date"
}


NUMBER_LABELS = {
    "premium", "liability", "ins_prem", "ins_otv", "timespent", "amount"
}


def _ci_get(d: dict, *keys: str):
    for k in keys:
        if k in d:
            return d[k]
        lk = k.lower()
        if lk in d:
            return d[lk]
        uk = k.upper()
        if uk in d:
            return d[uk]
    return None


def _human_label(key: str) -> str:
    lk = str(key).lower()
    return LABEL_MAP.get(lk, str(key))


def _fmt_num(val, decimals: int = 2, trim: bool = True) -> str:
    try:
        num = float(val)
    except Exception:
        return str(val)
    if math.isclose(num, round(num)):
        return f"{int(round(num)):,}".replace(",", " ")
    s = f"{num:,.{decimals}f}".replace(",", " ")
    if trim:
        s = s.rstrip("0").rstrip(".")
    return s


def _fmt_date(val) -> str:
    if val is None or str(val).strip() in {"", "None", "nan", "NaT"}:
        return "-"
    if isinstance(val, pd.Timestamp):
        dt = val.to_pydatetime()
    elif isinstance(val, datetime):
        dt = val
    elif isinstance(val, date):
        dt = datetime.combine(val, datetime.min.time())
    else:
        s = str(val).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S.%f"):
            try:
                dt = datetime.strptime(s, fmt)
                break
            except Exception:
                dt = None
        if dt is None:
            return s
    return dt.strftime("%d.%m.%Y %H:%M:%S")


def _format_value(key: str, val):
    if val is None or str(val).strip() in {"", "None", "nan", "NaT"}:
        return "-"
    lk = str(key).lower()
    if lk in DATE_LABELS or "date" in lk:
        return _fmt_date(val)
    if lk in NUMBER_LABELS:
        return _fmt_num(val)
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return _fmt_num(val)
    return str(val)


def _safe_contracts_dataframe(filters: dict) -> pd.DataFrame:
    try:
        rows = ContractsService().list_contracts(
            search=filters.get("search") or None,
            date_field=filters.get("date_field", "issue_date"),
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
        )
        df = pd.DataFrame(rows)
    except Exception as exc:
        st.error(f"Ошибка загрузки договоров: {exc}")
        return pd.DataFrame()

    if df.empty:
        return df

    rename_map = {
        "policy_issued": "Полис",
        "contract_id": "ID",
        "branch_name": "Филиал",
        "division_name": "Подразделение",
        "policy_no": "Полис",
        "contract_no": "№ договора",
        "code": "Код",
        "checked_flag": "Проверено",
        "insurance_product": "Страховой продукт",
        "client_name": "Страхователь",
        "phones": "Телефоны",
        "address": "Адрес",
        "beneficiary": "Бенефициар",
        "issue_date": "Дата заключения",
        "start_date": "Начало страх.",
        "end_date": "Конец страх.",
        "liability": "Ответственность",
        "liability_sum": "Ответств. в сумах",
        "transhi": "Транши",
        "premium": "Премия",
        "premium_sum": "Премия в сумах",
        "fact_received": "Факт.поступ.",
        "policy_premium": "Полис премия",
        "refund_sum": "Возврат в сумах",
        "last_payment_date": "Дата посл.оплаты",
        "payment_condition": "Условия оплаты",
        "risk_class": "Класс",
        "created_by": "Создал",
        "created_at": "Дата создания",
        "updated_at": "Дата посл.изменения",
        "commission": "Комиссионка",
        "total_losses": "Всего убытков",
        "last_claim_date": "Дата посл.событии",
        "total_paid": "Всего выплачено",
        "last_payout_date": "Дата посл.выплаты",
        "rate": "Ставка",
        "region_name": "Регион",
        "payment_type_name": "Тип оплаты",
        "files_count": "Файлы",
        "lessee_name": "Заёмщик/Лизингополучатель",
        "requisites": "Реквизит",
        "birthdate": "Дата рождения",
        "active_flag": "Актив",
        "beneficiary_mfo": "Бен.МФО",
        "declaration": "Декларация",
        "old_contract_no": "Старый № договора",
        "property_address": "Имущ.адрес",
        "borrower_pinfl": "Заёмщик ПИНФЛ",
        "borrower_doc": "Заёмщик Пасп./ИНН",
        "lot_id": "Лот ID",
        "insured_country": "Страна страхователя",
        "client_id": "Клиент ID",
        "insurance_type_id": "Вид страхования",
    "insurance_type_name": "Вид страхования",
    "insurance_object": "Объект страхования",
    "insurance_class": "Класс страхования",
    "product_code": "Код продукта",
    "division_name": "Подразделение",
    "currency_name": "Валюта",
    "amount_paid": "Поступившая сумма",
    "amount_paid_display": "Поступившая сумма",
    "premium_display": "Премия",
    "liability_display": "Ответственность",
        "status": "Статус",
    }
    df = df.rename(columns=rename_map)
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    wanted = [
        "Полис", "ID", "№ договора", "Страхователь", "Дата заключения", "Начало страх.", "Конец страх.",
        "Премия", "Ответственность", "Адрес", "Бенефициар", "Клиент ID", "Вид страхования", "Статус",
        "Филиал", "Подразделение", "Код", "Проверено", "Страховой продукт", "Телефоны",
        "Ответств. в сумах", "Транши", "Премия в сумах", "Факт.поступ.", "Полис премия",
        "Возврат в сумах", "Дата посл.оплаты", "Условия оплаты", "Класс", "Создал", "Дата создания",
        "Дата посл.изменения", "Комиссионка", "Всего убытков", "Дата посл.событии", "Всего выплачено",
        "Дата посл.выплаты", "Ставка", "Регион", "Тип оплаты", "Файлы", "Заёмщик/Лизингополучатель",
        "Реквизит", "Дата рождения", "Актив", "Бен.МФО", "Декларация", "Старый № договора", "Имущ.адрес",
        "Заёмщик ПИНФЛ", "Заёмщик Пасп./ИНН", "Лот ID", "Страна страхователя"
    ]
    existing = []
    seen = set()
    for c in wanted:
        if c in df.columns and c not in seen:
            existing.append(c)
            seen.add(c)
    df = df.loc[:, existing]
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]
    df = df.replace({None: pd.NA, "None": pd.NA, "": pd.NA})
    keep_cols = []
    for col in df.columns:
        series_or_df = df[col]
        if hasattr(series_or_df, "columns"):
            series_or_df = series_or_df.iloc[:, 0]
        if not series_or_df.isna().all():
            keep_cols.append(col)
    ordered_core = [
        "Полис", "ID", "№ договора", "Страхователь", "Дата заключения", "Начало страх.", "Конец страх.",
        "Премия", "Ответственность", "Адрес", "Бенефициар", "Клиент ID", "Вид страхования", "Статус"
    ]
    final_cols = [c for c in ordered_core if c in keep_cols] + [c for c in keep_cols if c not in ordered_core]
    df = df[final_cols]
    if "Полис" in df.columns:
        def _policy_icon(v):
            try:
                return "📄✅" if int(float(v)) > 0 else "📄❌"
            except Exception:
                return "📄❌"
        df["Полис"] = df["Полис"].apply(_policy_icon)
    base_url = "?" + urlencode({"page": "contracts"}) + "&contract_id="
    df["ID"] = df["ID"].apply(lambda x: f"{base_url}{int(x)}" if pd.notna(x) else "")
    return df




def _contracts_charts(df: pd.DataFrame) -> None:
    if df is None or df.empty or "Вид страхования" not in df.columns:
        return
    chart_df = df.copy()
    chart_df["Вид страхования"] = chart_df["Вид страхования"].fillna("-").astype(str).str.strip()
    chart_df = chart_df[chart_df["Вид страхования"] != ""]
    if chart_df.empty:
        return

    def _to_num(series_name: str) -> pd.Series:
        if series_name not in chart_df.columns:
            return pd.Series([0] * len(chart_df), index=chart_df.index, dtype=float)
        s = chart_df[series_name]
        if pd.api.types.is_numeric_dtype(s):
            return pd.to_numeric(s, errors="coerce").fillna(0)
        return pd.to_numeric(
            s.astype(str).str.replace(" ", "", regex=False).str.replace(",", ".", regex=False),
            errors="coerce",
        ).fillna(0)

    chart_df["_premium_sum"] = _to_num("Премия в сумах")
    if chart_df["_premium_sum"].sum() == 0:
        chart_df["_premium_sum"] = _to_num("Премия")

    grouped = (
        chart_df.groupby("Вид страхования", dropna=False)
        .agg(Количество=("Вид страхования", "size"), Сумма=("_premium_sum", "sum"))
        .reset_index()
        .sort_values(["Количество", "Сумма"], ascending=[False, False])
    )
    if grouped.empty:
        return

    st.subheader("Диаграммы по видам страхования")
    left, right = st.columns([1.2, 1])
    with left:
        fig_bar = px.bar(
            grouped,
            x="Вид страхования",
            y="Количество",
            title="Количество договоров по видам страхования",
            text="Количество",
        )
        fig_bar.update_traces(hovertemplate="%{x}<br>Количество: %{y}<extra></extra>")
        fig_bar.update_layout(height=380, margin=dict(l=10, r=10, t=55, b=120), xaxis_title=None, yaxis_title="Количество")
        fig_bar.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_bar, use_container_width=True)
    with right:
        pie_df = grouped[grouped["Сумма"] > 0].copy()
        if pie_df.empty:
            pie_df = grouped.copy()
            pie_df["Сумма"] = pie_df["Количество"]
            pie_title = "Доля по количеству договоров"
            hover = "%{label}<br>Количество: %{value}<br>Доля: %{percent}<extra></extra>"
        else:
            pie_title = "Доля по сумме премии"
            hover = "%{label}<br>Сумма: %{value:,.0f}<br>Доля: %{percent}<extra></extra>"
        fig_pie = px.pie(
            pie_df,
            names="Вид страхования",
            values="Сумма",
            title=pie_title,
            hole=0.45,
        )
        fig_pie.update_traces(textinfo="percent", hovertemplate=hover)
        fig_pie.update_layout(height=380, margin=dict(l=10, r=10, t=55, b=30), legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

def _compact_height(rows: int, row_px: int = 35, min_h: int = 90, max_h: int = 360) -> int:
    return max(min_h, min(max_h, row_px * (max(rows, 1) + 1)))


def _split_api_name(api_name: str | None) -> dict:
    s = (api_name or '').strip()
    if not s:
        return {"host": "-", "path": "-", "module": "-", "endpoint": "-"}
    try:
        parsed = urlparse(s)
        host = parsed.netloc or '-'
        path = parsed.path or s
        parts = [x for x in path.split('/') if x]
        endpoint = parts[-1] if parts else '-'
        module = '/'.join(parts[:-1]) if len(parts) > 1 else '-'
        return {"host": host, "path": path, "module": module, "endpoint": endpoint}
    except Exception:
        return {"host": "-", "path": s, "module": "-", "endpoint": s}


def _detail_table(d: dict, keys: list[str]) -> pd.DataFrame:
    items = []
    for key in keys:
        val = _ci_get(d, key, key.upper())
        if val is None or str(val).strip() in {"", "None", "nan", "NaT"}:
            continue
        items.append(( _human_label(key), _format_value(key, val) ))
    return pd.DataFrame(items, columns=["Поле", "Значение"])




@st.cache_data(show_spinner=False, ttl=300)
def _cached_contract_detail(contract_id: int) -> dict | None:
    return ContractsService().get_contract_detail(contract_id)


@st.cache_data(show_spinner=False, ttl=300)
def _cached_contract_policies(contract_id: int) -> list[dict]:
    return ContractsService().get_contract_policies(contract_id)


@st.cache_data(show_spinner=False, ttl=300)
def _cached_contract_payments(contract_id: int) -> list[dict]:
    return ContractsService().get_contract_payments(contract_id)


@st.cache_data(show_spinner=False, ttl=300)
def _cached_contract_api_logs(contract_id: int) -> list[dict]:
    return ContractsService().get_contract_api_logs(contract_id)


@st.cache_data(show_spinner=False, ttl=300)
def _cached_contract_api_log_detail(log_id: int) -> dict | None:
    return ContractsService().get_contract_api_log_detail(log_id)


def _render_contract_detail(contract_id: int) -> None:
    detail = _cached_contract_detail(contract_id)
    if not detail:
        st.warning("Договор не найден.")
        return

    st.markdown("### Карточка договора")
    top1, top2, top3, top4 = st.columns(4)
    top1.metric("ID", f"{_ci_get(detail, 'contract_id', 'CONTRACT_ID') or contract_id}")
    top2.metric("№ договора", f"{_format_value('contract_no', _ci_get(detail, 'contract_no', 'CONTRACT_NO', 'ins_num', 'INS_NUM'))}")
    top3.metric("Страхователь", f"{_format_value('client_name', _ci_get(detail, 'client_name', 'CLIENT_NAME'))}")
    top4.metric("Клиент ID", f"{_format_value('client_id', _ci_get(detail, 'client_id', 'CLIENT_ID', 'owner', 'OWNER'))}")

    currency_name = _ci_get(detail, "currency_name", "CURRENCY_NAME")
    premium_raw = _ci_get(detail, "premium", "PREMIUM", "ins_prem", "INS_PREM")
    liability_raw = _ci_get(detail, "liability", "LIABILITY", "ins_otv", "INS_OTV")
    amount_paid_raw = _ci_get(detail, "amount_paid", "AMOUNT_PAID")
    currency_suffix = ""
    if currency_name and str(currency_name).strip() not in {"", "None"}:
        currency_suffix = f" ({currency_name})"
    detail["premium_display"] = f"{_format_value('premium', premium_raw)}{currency_suffix}" if premium_raw is not None else "-"
    detail["liability_display"] = f"{_format_value('liability', liability_raw)}{currency_suffix}" if liability_raw is not None else "-"
    detail["amount_paid_display"] = f"{_format_value('amount_paid', amount_paid_raw)}{currency_suffix}" if amount_paid_raw is not None else "-"

    left_keys = [
        "contract_id", "client_id", "client_name", "created_by", "division_name",
        "insurance_type_name", "insurance_object", "insurance_class", "product_code"
    ]
    right_keys = [
        "status", "ins_num", "ins_date", "ins_datef", "ins_datet",
        "liability_display", "premium_display", "amount_paid_display", "currency_name"
    ]
    left, right = st.columns([1, 1])
    with left:
        show_df = _detail_table(detail, left_keys)
        st.dataframe(show_df, use_container_width=True, hide_index=True, height=_compact_height(min(len(show_df), 10), max_h=340))
    with right:
        raw_df = _detail_table(detail, right_keys)
        st.dataframe(raw_df, use_container_width=True, hide_index=True, height=_compact_height(min(len(raw_df), 10), max_h=340))

    tabs = st.tabs(["Полисы", "Оплаты", "Журнал API"])
    with tabs[0]:
        policies = pd.DataFrame(_cached_contract_policies(contract_id))
        if policies.empty:
            st.caption("Связанные полисы не найдены.")
        else:
            for col in policies.columns:
                policies[col] = policies[col].apply(lambda v, c=col: _format_value(c, v))
            st.dataframe(policies, use_container_width=True, hide_index=True, height=_compact_height(len(policies), max_h=220))
    with tabs[1]:
        payments = pd.DataFrame(_cached_contract_payments(contract_id))
        if payments.empty:
            st.caption("Связанные оплаты не найдены.")
        else:
            for col in payments.columns:
                payments[col] = payments[col].apply(lambda v, c=col: _format_value(c, v))
            st.dataframe(payments, use_container_width=True, hide_index=True, height=_compact_height(len(payments), max_h=220))

    with tabs[2]:
        api_logs = pd.DataFrame(_cached_contract_api_logs(contract_id))
        if api_logs.empty:
            st.caption("По этому договору API-журнал не найден.")
        else:
            logs_df = api_logs.copy().rename(columns={
                "log_id": "LOG_ID",
                "log_date": "Дата",
                "api_name": "API",
                "anketa_id": "ANKETA_ID",
                "polis_id": "POLIS_ID",
                "status_code": "HTTP",
                "reason_phrase": "Причина",
                "timespent": "Время",
                "error_code": "Код ошибки",
                "error_text": "Текст ошибки",
            })
            for col in logs_df.columns:
                logs_df[col] = logs_df[col].apply(lambda v, c=col: _format_value(c, v))
            st.caption(f"Показано строк: {len(logs_df)} из {len(logs_df)}")

            available_ids = [int(v) for v in api_logs.get("log_id", []).tolist() if pd.notna(v) and str(v).strip() not in ("", "None")]
            state_key = f"contract_api_log_id_{int(contract_id)}"
            cache_key = f"contract_api_log_cache_{int(contract_id)}"
            cache_ids_key = f"contract_api_log_cache_ids_{int(contract_id)}"
            if state_key not in st.session_state:
                st.session_state[state_key] = available_ids[0] if available_ids else None

            # Preload API log details once per contract to make switching between LOG_ID entries fast.
            current_ids = tuple(available_ids)
            if st.session_state.get(cache_ids_key) != current_ids:
                st.session_state[cache_ids_key] = current_ids
                st.session_state[cache_key] = {
                    int(log_id): _cached_contract_api_log_detail(int(log_id)) for log_id in available_ids
                }
            log_cache = st.session_state.get(cache_key, {})

            display_cols = ["LOG_ID", "Дата", "API", "ANKETA_ID", "POLIS_ID", "HTTP", "Причина", "Время", "Код ошибки", "Текст ошибки"]
            display_cols = [c for c in display_cols if c in logs_df.columns]

            if not logs_df.empty:
                header_cols = st.columns([1.0, 1.4, 3.2, 1.2, 1.0, 0.8, 1.6, 1.0, 1.2, 2.8][:len(display_cols)])
                for i, col_name in enumerate(display_cols):
                    header_cols[i].markdown(f"**{col_name}**")
                for row_idx, (_, row) in enumerate(logs_df[display_cols].iterrows()):
                    widths = [1.0, 1.4, 3.2, 1.2, 1.0, 0.8, 1.6, 1.0, 1.2, 2.8][:len(display_cols)]
                    row_cols = st.columns(widths)
                    raw_log_id = api_logs.iloc[row_idx].get("log_id")
                    for i, col_name in enumerate(display_cols):
                        if col_name == "LOG_ID" and pd.notna(raw_log_id):
                            if row_cols[i].button(str(row[col_name]), key=f"api_log_btn_{contract_id}_{int(raw_log_id)}"):
                                st.session_state[state_key] = int(raw_log_id)
                        else:
                            row_cols[i].write(row[col_name])
                    st.divider()

            selected_log_id = st.session_state.get(state_key)
            if selected_log_id:
                log_detail = log_cache.get(int(selected_log_id)) or _cached_contract_api_log_detail(int(selected_log_id))
                if log_detail:
                    api_name = str(_ci_get(log_detail, 'api_name', 'API_NAME') or '-')
                    api_parts = _split_api_name(api_name)
                    st.markdown(f"#### API-журнал #{selected_log_id}")
                    h1, h2, h3, h4, h5 = st.columns([2, 2, 2, 1, 1])
                    h1.metric("API / host", api_parts['host'])
                    h2.metric("Endpoint", api_parts['endpoint'])
                    h3.metric("Модуль", api_parts['module'])
                    h4.metric("HTTP", _format_value('status_code', _ci_get(log_detail, 'status_code', 'STATUS_CODE') or '-'))
                    h5.metric("Время", _format_value('timespent', _ci_get(log_detail, 'timespent', 'TIMESPENT') or '-'))
                    st.caption(f"URL: {api_name}")
                    meta_keys = ["log_date", "usr", "log_div", "anketa_id", "polis_id", "reason_phrase", "error_code", "error_text", "error_info", "http_version"]
                    meta_df = _detail_table(log_detail, meta_keys)
                    if not meta_df.empty:
                        st.dataframe(meta_df, use_container_width=True, hide_index=True, height=_compact_height(min(len(meta_df), 8), max_h=160))
                    lcol, rcol = st.columns(2)
                    with lcol:
                        st.markdown("##### Отправлено в фонд")
                        st.code(str(_ci_get(log_detail, "log_sent", "LOG_SENT") or ""), language="json")
                    with rcol:
                        st.markdown("##### Ответ из фонда")
                        st.code(str(_ci_get(log_detail, "log_received", "LOG_RECEIVED") or ""), language="json")


def render() -> None:
    render_header("Договоры", "APEX-аналоги: страницы 2, 13, 14")
    filters = get_sidebar_filters("contracts")

    started_at = time.perf_counter()
    progress_text = st.empty()
    progress = st.progress(0)
    progress_text.caption("Загрузка договоров...")
    progress.progress(20)
    df = _safe_contracts_dataframe(filters)
    progress.progress(100)
    elapsed = time.perf_counter() - started_at
    progress_text.caption(f"Время загрузки: {elapsed:.2f} сек.")

    st.caption(
        f"Показано записей: {len(df)}"
        + (
            f" | Период: {filters.get('date_from')} — {filters.get('date_to')}"
            if filters.get('date_from') and filters.get('date_to') else ""
        )
    )

    contract_id = st.query_params.get("contract_id")
    if isinstance(contract_id, list):
        contract_id = contract_id[0] if contract_id else None

    if contract_id:
        if st.button("Закрыть карточку"):
            if "contract_id" in st.query_params:
                del st.query_params["contract_id"]
            if "api_log_id" in st.query_params:
                del st.query_params["api_log_id"]
            st.rerun()
        _render_contract_detail(int(contract_id))
        return

    if df.empty:
        st.info("По выбранному фильтру договоры не найдены.")
    else:
        _contracts_charts(df)
        render_dataframe(
            df,
            key="contracts_table",
            height=760,
            column_config={
                "Полис": st.column_config.TextColumn(
                    "Полис",
                    help="📄✅ — полис выдан, 📄❌ — полис не выдан",
                    width="small",
                ),
                "ID": st.column_config.LinkColumn(
                    "ID",
                    help="Нажмите, чтобы открыть карточку договора",
                    display_text=r".*contract_id=(\d+)",
                )
            },
        )
