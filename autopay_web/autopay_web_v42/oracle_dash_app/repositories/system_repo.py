from __future__ import annotations

from oracle_dash_app.db.oracle_helpers import scalar, get_runtime_connection_info
from oracle_dash_app.sql.queries import ORACLE_INFO


class SystemRepository:
    def get_oracle_info(self) -> dict:
        result = get_runtime_connection_info().copy()
        for key, query in ORACLE_INFO.items():
            try:
                result[key] = scalar(query)
            except Exception as exc:
                result[key] = f"ERROR: {exc}"
        return result
