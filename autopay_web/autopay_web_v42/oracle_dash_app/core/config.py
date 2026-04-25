from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    app_title: str = os.getenv("APP_TITLE", "web_dastur_dashboard_temp")
    db_backend: str = os.getenv("APP_DB_BACKEND", "oracle").lower()
    sqlite_path: str = os.getenv("APP_SQLITE_PATH", "data/demo.db")

    oracle_user: str = os.getenv("APP_ORACLE_USER", "osago")
    oracle_password: str = os.getenv("APP_ORACLE_PASSWORD", "uzb")
    oracle_host: str = os.getenv("APP_ORACLE_HOST", "192.168.11.13")
    oracle_port: int = int(os.getenv("APP_ORACLE_PORT", "1521"))
    oracle_service: str = os.getenv("APP_ORACLE_SERVICE", "")
    oracle_sid: str = os.getenv("APP_ORACLE_SID", "")
    oracle_dsn: str = os.getenv("APP_ORACLE_DSN", "")
    oracle_autodetect: bool = os.getenv("APP_ORACLE_AUTODETECT", "true").lower() == "true"
    oracle_schema: str = os.getenv("APP_ORACLE_SCHEMA", "OSAGO")

    page_size: int = int(os.getenv("APP_PAGE_SIZE", "100"))
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    @property
    def oracle_candidate_services(self) -> list[str]:
        return _split_csv(os.getenv("APP_ORACLE_CANDIDATE_SERVICES", "FREEPDB1,ORCLPDB1,XEPDB1,FREE"))

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.sqlite_path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
