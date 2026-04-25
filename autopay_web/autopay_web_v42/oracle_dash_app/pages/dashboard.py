from __future__ import annotations

import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from oracle_dash_app.components.tables import render_dataframe
from oracle_dash_app.services.dashboard_service import DashboardService


NUMERIC_COLS = [
    "ALLPLAN", "MNPLAN", "YOPL", "MOPL", "OPL", "F_OSAGO", "F_OSGOR",
    "F_OSGOP", "F_OILA", "OPLPLUS", "F_OTHER", "HBOPL", "ONEDAY", "OBV",
    "MPERC", "YPERC", "FACT_AMOUNT", "PLAN_AMOUNT", "MONTH_PERCENT", "F_HALKBANK",
]

DISPLAY_COLUMNS = [
    "DIVISION_NAME", "ALLPLAN", "MNPLAN", "YOPL", "MOPL", "OPL", "ONEDAY",
    "OBV", "F_OSAGO", "F_OSGOR", "F_OSGOP", "F_OILA", "F_OTHER", "HBOPL",
    "MPERC", "YPERC",
]


def _safe(title: str, fn, default):
    try:
        return fn()
    except Exception as exc:
        st.warning(f"{title}: {exc}")
        return default


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    df.columns = [str(c).upper() for c in df.columns]
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["DIVISION_NAME", "MONTH_LABEL"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
    return df


def _format_value(v):
    try:
        return f"{float(v):,.2f}".replace(",", " ")
    except Exception:
        return v


def _inject_animation_css() -> None:
    st.markdown(
        """
        <style>
        .stPlotlyChart > div {animation: fadeInUp .45s ease both;}
        @keyframes fadeInUp {
            from {opacity: 0; transform: translateY(10px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    _inject_animation_css()

    started_at = time.perf_counter()
    progress_text = st.empty()
    progress = st.progress(0)
    progress_text.caption("Dashboard юкланмоқда...")

    service = DashboardService()
    progress.progress(20)
    df = _normalize(_safe("Dashboard plan/fact", lambda: service.get_plan_fact_df(), pd.DataFrame()))
    progress.progress(55)
    monthly_df = _normalize(_safe("Dashboard monthly", lambda: service.get_monthly_df(), pd.DataFrame()))
    progress.progress(85)

    if df.empty:
        progress.progress(100)
        elapsed = time.perf_counter() - started_at
        progress_text.caption(f"Юкланиш вақти: {elapsed:.2f} сек.")
        st.info("План/факт сўрови маълумот қайтармади. SP_DIVISION, INS_FORECAST ва VW_FACTOPL_ объектларини текширинг.")
        return

    total_allplan = float(df["ALLPLAN"].sum()) if "ALLPLAN" in df.columns else 0
    total_mnplan = float(df["MNPLAN"].sum()) if "MNPLAN" in df.columns else 0
    total_opl = float(df["OPL"].sum()) if "OPL" in df.columns else 0
    total_oneday = float(df["ONEDAY"].sum()) if "ONEDAY" in df.columns else 0
    total_remaining_month = max(total_mnplan - total_opl, 0)
    total_remaining_year = max(total_allplan - total_opl, 0)

    summary_cols = st.columns(6)
    items = [
        ("Факт (сўм)", total_opl),
        ("Ойлик режа (сўм)", total_mnplan),
        ("Ой учун қолдиқ (сўм)", total_remaining_month),
        ("Йиллик режа (сўм)", total_allplan),
        ("Йил учун қолдиқ (сўм)", total_remaining_year),
        ("Бугун (сўм)", total_oneday),
    ]
    for col, (label, value) in zip(summary_cols, items):
        col.metric(label, f"{value:,.0f}".replace(",", " "))

    progress.progress(100)
    elapsed = time.perf_counter() - started_at
    progress_text.caption(f"Юкланиш вақти: {elapsed:.2f} сек.")

    show_charts = st.checkbox("Диаграммаларни кўрсатиш", value=True)

    if show_charts:
        st.subheader("Диаграммалар")

        row1_left, row1_right = st.columns([1.05, 1.35])
        with row1_left:
            pie_df = df[df.get("OPL", 0) > 0].sort_values("OPL", ascending=False).copy()
            if not pie_df.empty:
                total = float(pie_df["OPL"].sum())
                pie_df["LABEL"] = pie_df["DIVISION_NAME"]
                pie_df["TEXT"] = pie_df["OPL"].apply(
                    lambda v: f"{(v / total * 100):.1f}%" if total and (v / total * 100) >= 4 else ""
                )
                division_color_sequence = [
                    "#156fc4", "#78b4e3", "#ff3131", "#f3a7a8", "#2cb1a1",
                    "#6ddc9f", "#ff9800", "#f2cf66", "#6f42c1", "#2f8eed",
                    "#d0d7e2", "#f48c8c", "#66d1c8", "#ffd166", "#f4b183",
                    "#b39ddb", "#a8c7fa", "#0b4f8a", "#00c2ff", "#23d160",
                ]
                fig1 = px.pie(
                    pie_df,
                    names="LABEL",
                    values="OPL",
                    title="Бўлинмалар кесимида факт",
                    hole=0.52,
                    color_discrete_sequence=division_color_sequence,
                )
                fig1.update_traces(
                    text=pie_df["TEXT"],
                    textinfo="text",
                    textfont=dict(size=14),
                    hovertemplate="%{label}<br>Факт: %{value:,.0f}<br>Улуш: %{percent}<extra></extra>",
                    sort=False,
                )
                fig1.update_layout(
                    height=420,
                    margin=dict(l=10, r=180, t=50, b=30),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=10),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                )
                st.plotly_chart(fig1, use_container_width=True)

        with row1_right:
            if not monthly_df.empty and {"MONTH_LABEL", "PLAN_AMOUNT", "FACT_AMOUNT", "MONTH_PERCENT"}.issubset(monthly_df.columns):
                mdf = monthly_df.copy()
                mdf["DISPLAY_MONTH"] = mdf["MONTH_LABEL"].astype(str)
                fig2 = make_subplots(specs=[[{"secondary_y": True}]])
                fig2.add_trace(
                    go.Bar(
                        x=mdf["DISPLAY_MONTH"],
                        y=mdf["PLAN_AMOUNT"],
                        name="Режа",
                        hovertemplate="%{x}<br>Режа: %{y:,.0f}<extra></extra>",
                    ),
                    secondary_y=False,
                )
                fig2.add_trace(
                    go.Bar(
                        x=mdf["DISPLAY_MONTH"],
                        y=mdf["FACT_AMOUNT"],
                        name="Факт",
                        hovertemplate="%{x}<br>Факт: %{y:,.0f}<extra></extra>",
                    ),
                    secondary_y=False,
                )
                fig2.add_trace(
                    go.Scatter(
                        x=mdf["DISPLAY_MONTH"],
                        y=mdf["MONTH_PERCENT"],
                        name="% бажарилиш",
                        mode="lines+markers+text",
                        line=dict(color="#ef4444", width=2),
                        text=[f"{v:.1f}%" for v in mdf["MONTH_PERCENT"]],
                        textposition="top center",
                        hovertemplate="%{x}<br>Бажарилиш: %{y:.2f}%<extra></extra>",
                    ),
                    secondary_y=True,
                )
                fig2.update_layout(
                    title="Ойлар кесимида режа / факт",
                    barmode="group",
                    height=420,
                    margin=dict(l=10, r=10, t=50, b=55),
                    legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0),
                )
                fig2.update_xaxes(title_text=None, type="category")
                fig2.update_yaxes(title_text="Сумма", secondary_y=False)
                fig2.update_yaxes(title_text="%", secondary_y=True)
                st.plotly_chart(fig2, use_container_width=True)

        row2_left, row2_right = st.columns([1.35, 0.9])
        with row2_left:
            if not monthly_df.empty and {"MONTH_LABEL", "F_OSAGO", "F_OSGOR", "F_OSGOP", "F_OILA", "F_HALKBANK", "F_OTHER"}.issubset(monthly_df.columns):
                fig4 = go.Figure()
                for col, label in [
                    ("F_OSAGO", "OSAGO"),
                    ("F_OSGOR", "OSGOR"),
                    ("F_OSGOP", "OSGOP"),
                    ("F_OILA", "OILA"),
                    ("F_HALKBANK", "Халқбанк"),
                    ("F_OTHER", "Бошқа"),
                ]:
                    fig4.add_trace(
                        go.Bar(
                            x=monthly_df["MONTH_LABEL"],
                            y=monthly_df[col],
                            name=label,
                            hovertemplate="%{x}<br>" + label + ": %{y:,.0f}<extra></extra>",
                        )
                    )
                fig4.update_layout(
                    title="Ойлар бўйича тушумлар",
                    barmode="stack",
                    height=350,
                    margin=dict(l=10, r=10, t=50, b=40),
                    legend=dict(orientation="h", yanchor="top", y=-0.17, xanchor="left", x=0),
                )
                fig4.update_xaxes(title_text=None, type="category")
                fig4.update_yaxes(title_text="Сумма")
                st.plotly_chart(fig4, use_container_width=True)

        with row2_right:
            if total_mnplan > 0:
                exec_df = pd.DataFrame([
                    {"label": "Бажарилди", "value": min(total_opl, total_mnplan)},
                    {"label": "Қолди", "value": total_remaining_month},
                ])
                fig3 = px.pie(
                    exec_df,
                    names="label",
                    values="value",
                    title="Ойлик режа бажарилиши",
                    hole=0.58,
                )
                fig3.update_traces(
                    textinfo="percent+label",
                    hovertemplate="%{label}<br>Сумма: %{value:,.0f}<br>Улуш: %{percent}<extra></extra>",
                )
                fig3.update_layout(
                    height=350,
                    margin=dict(l=10, r=10, t=50, b=30),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
                )
                fig3.add_annotation(
                    text=f"{(total_opl / total_mnplan * 100):.1f}%",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font_size=20,
                )
                st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Бўлинмалар кесимида режа / факт")
    table_df = df[[c for c in DISPLAY_COLUMNS if c in df.columns]].copy()
    rename_map = {
        "DIVISION_NAME": "Бўлинма",
        "ALLPLAN": "Йиллик режа",
        "MNPLAN": "Ойлик режа",
        "YOPL": "Кечаги факт",
        "MOPL": "Ойлик факт",
        "OPL": "Факт",
        "ONEDAY": "Бугун",
        "OBV": "Мажбурий",
        "F_OSAGO": "OSAGO",
        "F_OSGOR": "OSGOR",
        "F_OSGOP": "OSGOP",
        "F_OILA": "OILA",
        "F_OTHER": "Бошқа",
        "HBOPL": "HB",
        "MPERC": "% ой",
        "YPERC": "% йил",
    }
    table_df = table_df.rename(columns=rename_map)

    numeric_cols = [c for c in table_df.columns if c != "Бўлинма"]
    totals_row = {"Бўлинма": "ЖАМИ"}
    for col in numeric_cols:
        source_col = next((k for k,v in rename_map.items() if v == col), None)
        if source_col and source_col in df.columns:
            totals_row[col] = float(df[source_col].sum())
        else:
            totals_row[col] = 0.0

    if " % месяц" in totals_row:
        totals_row["% месяц"] = 0.0
    if "% месяц" in totals_row:
        totals_row["% месяц"] = (total_opl / total_mnplan * 100) if total_mnplan else 0.0
    if "% год" in totals_row:
        totals_row["% год"] = (total_opl / total_allplan * 100) if total_allplan else 0.0

    totals_df = pd.DataFrame([totals_row])

    division_color_sequence = [
        "#156fc4", "#78b4e3", "#ff3131", "#f3a7a8", "#2cb1a1",
        "#6ddc9f", "#ff9800", "#f2cf66", "#6f42c1", "#2f8eed",
        "#d0d7e2", "#f48c8c", "#66d1c8", "#ffd166", "#f4b183",
        "#b39ddb", "#a8c7fa", "#0b4f8a", "#00c2ff", "#23d160",
    ]
    top5_names = []
    top5_color_map = {}
    if "Факт" in table_df.columns:
        try:
            top5_names = (
                table_df.sort_values("Факт", ascending=False)
                .head(5)["Бўлинма"].astype(str).tolist()
            )
            top5_color_map = {
                name: division_color_sequence[idx % len(division_color_sequence)]
                for idx, name in enumerate(top5_names)
            }
        except Exception:
            top5_names = []
            top5_color_map = {}

    table_df = pd.concat([table_df, totals_df], ignore_index=True)

    display_df = table_df.copy()
    for col in display_df.columns:
        if col != "Бўлинма":
            display_df[col] = display_df[col].map(_format_value)

    total_bg = "#dbeafe"
    zebra_row_even = "#f8fafc"
    zebra_row_odd = "#eef4ff"
    zebra_col_even = "#ffffff"
    zebra_col_odd = "#f3f7ff"
    header_bg_even = "#0f5aa0"
    header_bg_odd = "#0f5aa0"

    def _mix_hex(c1: str, c2: str) -> str:
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        rgb1 = tuple(int(c1[i:i+2], 16) for i in (0, 2, 4))
        rgb2 = tuple(int(c2[i:i+2], 16) for i in (0, 2, 4))
        mixed = tuple(int((a + b) / 2) for a, b in zip(rgb1, rgb2))
        return "#%02x%02x%02x" % mixed

    def _style_table(dataframe):
        styles = pd.DataFrame("", index=dataframe.index, columns=dataframe.columns)

        for row_idx in dataframe.index:
            row_name = str(dataframe.at[row_idx, "Бўлинма"]).strip().upper()
            if row_name == "ЖАМИ":
                styles.loc[row_idx, :] = [
                    f"background-color: {total_bg}; font-weight: 700; border-top: 2px solid #93c5fd; border-bottom: 2px solid #93c5fd"
                    for _ in dataframe.columns
                ]
                continue

            top_bg = top5_color_map.get(str(dataframe.at[row_idx, "Бўлинма"]))
            if top_bg:
                for col_name in dataframe.columns:
                    styles.at[row_idx, col_name] = f"background-color: {top_bg}; color: #ffffff; font-weight: 700"
                continue

            row_bg = zebra_row_even if row_idx % 2 == 0 else zebra_row_odd
            for col_idx, col_name in enumerate(dataframe.columns):
                col_bg = zebra_col_even if col_idx % 2 == 0 else zebra_col_odd
                bg = _mix_hex(row_bg, col_bg)
                styles.at[row_idx, col_name] = f"background-color: {bg}"

        return styles

    header_styles = [
        {"selector": "thead th", "props": f"background-color: {header_bg_even} !important; color: #ffffff !important; font-weight: 700 !important; border-bottom: 1px solid #1d4ed8;"},
        {"selector": "thead tr th", "props": f"background-color: {header_bg_even} !important; color: #ffffff !important; font-weight: 700 !important;"},
        {"selector": "th.col_heading", "props": f"background-color: {header_bg_even} !important; color: #ffffff !important; font-weight: 700 !important;"},
        {"selector": "th.blank", "props": f"background-color: {header_bg_even} !important; color: #ffffff !important;"},
        {"selector": ".col_heading", "props": f"background-color: {header_bg_even} !important; color: #ffffff !important; font-weight: 700 !important;"},
        {"selector": "tbody td", "props": "border-color: #dbe3f0;"},
    ]

    styled = (
        display_df.style
        .apply(_style_table, axis=None)
        .set_properties(**{"text-align": "left"}, subset=["Бўлинма"])
        .set_table_styles(header_styles, overwrite=False)
    )
    row_count = len(display_df.index)
    auto_height = min(max(80 + row_count * 35, 320), 1450)
    st.dataframe(styled, use_container_width=True, hide_index=True, height=auto_height)
