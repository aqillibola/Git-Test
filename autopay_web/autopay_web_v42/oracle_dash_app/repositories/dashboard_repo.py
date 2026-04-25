from __future__ import annotations

import pandas as pd

from oracle_dash_app.db.oracle_helpers import scalar
from oracle_dash_app.repositories.base import BaseRepository
from oracle_dash_app.sql.queries import DASHBOARD_METRICS, DASHBOARD_PLAN_FACT, DASHBOARD_MONTHLY


class DashboardRepository(BaseRepository):
    def get_metrics(self) -> dict:
        return {
            "clients": int(scalar(DASHBOARD_METRICS["clients"]) or 0),
            "contracts": int(scalar(DASHBOARD_METRICS["contracts"]) or 0),
            "policies": int(scalar(DASHBOARD_METRICS["policies"]) or 0),
            "payments_total": float(scalar(DASHBOARD_METRICS["payments_total"]) or 0),
        }

    def get_plan_fact_df(self) -> pd.DataFrame:
        return self.fetch_df(DASHBOARD_PLAN_FACT)


    def get_monthly_df(self) -> pd.DataFrame:
        return self.fetch_df(DASHBOARD_MONTHLY)
