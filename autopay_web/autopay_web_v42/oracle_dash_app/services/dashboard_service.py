from __future__ import annotations

import pandas as pd
from oracle_dash_app.repositories.dashboard_repo import DashboardRepository


class DashboardService:
    def __init__(self) -> None:
        self.repo = DashboardRepository()

    def get_metrics(self) -> dict:
        return self.repo.get_metrics()

    def get_plan_fact_df(self) -> pd.DataFrame:
        return self.repo.get_plan_fact_df()


    def get_monthly_df(self) -> pd.DataFrame:
        return self.repo.get_monthly_df()
