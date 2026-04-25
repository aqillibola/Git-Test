from __future__ import annotations

import pandas as pd
import streamlit as st


def _auto_height(total_rows: int, min_height: int = 220, max_height: int = 900) -> int:
    estimated = 42 + (total_rows + 1) * 35
    return max(min_height, min(max_height, estimated))


def render_df(rows: list[dict], use_container_width: bool = True, key: str = "table", height: int | None = None) -> None:
    df = pd.DataFrame(rows)
    render_dataframe(df, key=key, use_container_width=use_container_width, height=height)


def render_dataframe(df, key: str = "table", use_container_width: bool = True, height: int | None = None, column_config: dict | None = None) -> None:
    if df is None:
        df = pd.DataFrame()
    source = df.data if hasattr(df, "data") else df
    if isinstance(source, pd.DataFrame):
        view_source = source.copy()
        total = len(source)
    else:
        view_source = source
        total = 0
    st.caption(f"Показано строк: {total}")
    frame_height = height if height is not None else _auto_height(total)
    if hasattr(df, "data") and isinstance(df.data, pd.DataFrame):
        styler = view_source.style
        try:
            styler = styler._copy(df)
            styler.data = view_source
        except Exception:
            pass
        st.dataframe(styler, use_container_width=use_container_width, hide_index=True, height=frame_height, column_config=column_config)
    else:
        st.dataframe(view_source, use_container_width=use_container_width, hide_index=True, height=frame_height, column_config=column_config)
