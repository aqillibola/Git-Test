from __future__ import annotations

from functools import lru_cache
from typing import Any

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.engine import Engine

from oracle_dash_app.core.config import get_settings


_DISCOVERED: dict[str, Any] = {
    "backend": None,
    "host": None,
    "port": None,
    "schema": None,
    "service_name": None,
    "dsn": None,
}


def _engine_from_url(url: str) -> Engine:
    return sa.create_engine(url, future=True, pool_pre_ping=True)


def _oracle_url_from_service(host: str, port: int, user: str, password: str, service_name: str) -> str:
    return f"oracle+oracledb://{user}:{password}@{host}:{port}/?service_name={service_name}"


def _oracle_url_from_sid(host: str, port: int, user: str, password: str, sid: str) -> str:
    return f"oracle+oracledb://{user}:{password}@{host}:{port}/?sid={sid}"


def _oracle_url_from_dsn(user: str, password: str, dsn: str) -> str:
    return f"oracle+oracledb://{user}:{password}@{dsn}"


def _test_engine(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(sa.text("select 1 from dual"))


def _discover_oracle_engine() -> Engine:
    settings = get_settings()
    tried: list[str] = []

    if settings.oracle_dsn:
        url = _oracle_url_from_dsn(settings.oracle_user, settings.oracle_password, settings.oracle_dsn)
        tried.append(f"dsn={settings.oracle_dsn}")
        engine = _engine_from_url(url)
        _test_engine(engine)
        _DISCOVERED.update({
            "backend": "oracle",
            "host": settings.oracle_host,
            "port": settings.oracle_port,
            "schema": settings.oracle_schema,
            "service_name": settings.oracle_dsn,
            "dsn": settings.oracle_dsn,
        })
        return engine

    if settings.oracle_service:
        url = _oracle_url_from_service(
            settings.oracle_host,
            settings.oracle_port,
            settings.oracle_user,
            settings.oracle_password,
            settings.oracle_service,
        )
        tried.append(f"service={settings.oracle_service}")
        try:
            engine = _engine_from_url(url)
            _test_engine(engine)
            _DISCOVERED.update({
                "backend": "oracle",
                "host": settings.oracle_host,
                "port": settings.oracle_port,
                "schema": settings.oracle_schema,
                "service_name": settings.oracle_service,
                "dsn": url,
            })
            return engine
        except Exception:
            pass

    if settings.oracle_sid:
        url = _oracle_url_from_sid(
            settings.oracle_host,
            settings.oracle_port,
            settings.oracle_user,
            settings.oracle_password,
            settings.oracle_sid,
        )
        tried.append(f"sid={settings.oracle_sid}")
        try:
            engine = _engine_from_url(url)
            _test_engine(engine)
            _DISCOVERED.update({
                "backend": "oracle",
                "host": settings.oracle_host,
                "port": settings.oracle_port,
                "schema": settings.oracle_schema,
                "service_name": settings.oracle_sid,
                "dsn": url,
            })
            return engine
        except Exception:
            pass

    if settings.oracle_autodetect:
        for service_name in settings.oracle_candidate_services:
            url = _oracle_url_from_service(
                settings.oracle_host,
                settings.oracle_port,
                settings.oracle_user,
                settings.oracle_password,
                service_name,
            )
            tried.append(f"service={service_name}")
            try:
                engine = _engine_from_url(url)
                _test_engine(engine)
                _DISCOVERED.update({
                    "backend": "oracle",
                    "host": settings.oracle_host,
                    "port": settings.oracle_port,
                    "schema": settings.oracle_schema,
                    "service_name": service_name,
                    "dsn": url,
                })
                return engine
            except Exception:
                continue

    tried_str = ", ".join(tried) if tried else "no attempts"
    raise RuntimeError(
        "Oracle connection failed. Set APP_ORACLE_DSN or APP_ORACLE_SERVICE in .env. "
        f"Tried: {tried_str}"
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    if settings.db_backend == "sqlite":
        _DISCOVERED.update({
            "backend": "sqlite",
            "host": None,
            "port": None,
            "schema": None,
            "service_name": None,
            "dsn": settings.sqlite_url,
        })
        return _engine_from_url(settings.sqlite_url)
    return _discover_oracle_engine()


def get_runtime_connection_info() -> dict[str, Any]:
    settings = get_settings()
    return {
        "backend": _DISCOVERED.get("backend") or settings.db_backend,
        "host": _DISCOVERED.get("host") or settings.oracle_host,
        "port": _DISCOVERED.get("port") or settings.oracle_port,
        "schema": _DISCOVERED.get("schema") or settings.oracle_schema,
        "service_name": _DISCOVERED.get("service_name"),
        "dsn": _DISCOVERED.get("dsn"),
    }



@lru_cache(maxsize=128)
def get_table_columns(table_name: str) -> set[str]:
    settings = get_settings()
    engine = get_engine()
    sql_text = """
        select upper(column_name)
        from all_tab_columns
        where owner = upper(:owner)
          and table_name = upper(:table_name)
    """
    with engine.connect() as conn:
        rows = conn.execute(sa.text(sql_text), {"owner": settings.oracle_schema, "table_name": table_name}).fetchall()
    return {str(r[0]).upper() for r in rows}


def column_exists(table_name: str, column_name: str) -> bool:
    if get_settings().db_backend == "sqlite":
        return True
    return column_name.upper() in get_table_columns(table_name)


def first_existing_column(table_name: str, candidates: list[str]) -> str | None:
    if get_settings().db_backend == "sqlite":
        return candidates[0] if candidates else None
    cols = get_table_columns(table_name)
    for candidate in candidates:
        if candidate.upper() in cols:
            return candidate
    return None

def read_sql_df(sql_text: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(sa.text(sql_text), conn, params=params or {})


def scalar(sql_text: str, params: dict[str, Any] | None = None) -> Any:
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(sa.text(sql_text), params or {}).scalar()


def get_active_sessions_count() -> int | None:
    if get_settings().db_backend == "sqlite":
        return None
    queries = [
        "select count(*) from v$session where type = 'USER' and status = 'ACTIVE'",
        "select count(*) from gv$session where type = 'USER' and status = 'ACTIVE'",
    ]
    for q in queries:
        try:
            value = scalar(q)
            return int(value) if value is not None else None
        except Exception:
            continue
    return None
