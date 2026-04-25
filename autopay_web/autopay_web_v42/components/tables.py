import io
from datetime import datetime
import pandas as pd
import streamlit as st


def format_money_and_date_columns(df):
    format_dict = {}
    money_keywords = [
        "сумма", "қарз", "amount", "просрочки", "overdue", "долг",
        "кредита", "списано", "ечилган", "кредит", "қолдиқ"
    ]
    date_keywords = [
        "вақт", "дата", "time", "date", "created_at", "pay_time",
        "сана", "снятие", "ечиш"
    ]

    for col in df.columns:
        col_lower = col.lower()

        if any(kw in col_lower for kw in money_keywords):
            format_dict[col] = lambda x: f"{x:,.2f}".replace(",", " ") if pd.notna(x) and x != "" else ""

        elif any(kw in col_lower for kw in date_keywords):
            def format_datetime(x):
                if pd.isna(x):
                    return ""
                try:
                    dt = pd.to_datetime(x) if isinstance(x, str) else x
                    months_uz = {
                        1: "январь", 2: "февраль", 3: "март", 4: "апрель",
                        5: "май", 6: "июнь", 7: "июль", 8: "август",
                        9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"
                    }
                    month_name = months_uz.get(dt.month, "ой")
                    return f"{dt.day} {month_name} {dt.year} йил соат {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
                except Exception:
                    return str(x)

            format_dict[col] = format_datetime

        elif pd.api.types.is_numeric_dtype(df[col]):
            format_dict[col] = lambda x: (
                f"{int(x):,}".replace(",", " ")
                if pd.notna(x) and isinstance(x, (int, float)) and x == int(x)
                else x
            )

    return format_dict


def display_dataframe(df, height=800):
    if df.empty:
        st.info("ℹ️ Маълумот мавжуд эмас.")
        return

    if "№" not in df.columns:
        df.insert(0, "№", range(1, len(df) + 1))

    df_display = df.head(1000).copy() if len(df) > 1000 else df.copy()

    with st.expander("📄 Жадвални кўриш", expanded=True):
        format_dict = format_money_and_date_columns(df_display)

        def highlight_row(row):
            debt_col = None
            for name in ["Қолдиқ қарз", "Остаток долга", "Қарз"]:
                if name in row.index:
                    debt_col = name
                    break
            if debt_col:
                try:
                    debt = float(row[debt_col])
                    if debt < 0:
                        return ["background-color: #FDE8C9; color: #501C4C"] * len(row)
                    elif debt == 0:
                        return ["background-color: #DFFCAC; color: #436E5B"] * len(row)
                except Exception:
                    pass
            return [""] * len(row)

        styled_df = df_display.style.format(format_dict).apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=height, hide_index=True)

        col1, col2 = st.columns(2)
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        with col1:
            st.download_button(
                "📥 CSV юклаш",
                csv,
                f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv",
                use_container_width=True,
            )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Маълумотлар")

        with col2:
            st.download_button(
                "📊 Excel юклаш",
                buffer.getvalue(),
                f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
