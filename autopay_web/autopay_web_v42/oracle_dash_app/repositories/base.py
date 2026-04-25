from __future__ import annotations

from typing import Any
import pandas as pd
from oracle_dash_app.db.oracle_helpers import read_sql_df


class BaseRepository:
    def fetch_df(self, sql_text: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        return read_sql_df(sql_text, params=params)

    def fetch_rows(self, sql_text: str, params: dict[str, Any] | None = None) -> list[dict]:
        df = self.fetch_df(sql_text, params=params)
        return df.to_dict(orient="records")
