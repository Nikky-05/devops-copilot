from functools import lru_cache

import psycopg
from langchain_core.tools import BaseTool, tool
from psycopg.rows import dict_row

from app.utils.config import get_settings

_READ_ONLY_PREFIXES = ("SELECT", "WITH", "EXPLAIN", "SHOW")


@lru_cache(maxsize=1)
def _conn() -> psycopg.Connection:
    return psycopg.connect(get_settings().postgres_url, autocommit=True)


def _fetch(query: str, params: tuple = ()) -> list[dict]:
    with _conn().cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        return cur.fetchall()


@tool
def pg_list_tables() -> list[str]:
    """List tables in the public schema of the connected Postgres database."""
    rows = _fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
    )
    return [r["tablename"] for r in rows]


@tool
def pg_describe_table(name: str) -> list[dict]:
    """Return column name, type, and nullability for a table in the public schema."""
    return _fetch(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position",
        (name,),
    )


@tool
def pg_read_query(query: str, limit: int = 100) -> list[dict]:
    """Execute a READ-ONLY SQL query (SELECT/WITH/EXPLAIN/SHOW) and return up to `limit` rows."""
    head = query.strip().upper().split(None, 1)[0] if query.strip() else ""
    if head not in _READ_ONLY_PREFIXES:
        raise ValueError("Only read-only queries are permitted (SELECT/WITH/EXPLAIN/SHOW).")
    return _fetch(query)[:limit]


def get_postgres_tools() -> list[BaseTool]:
    if not get_settings().postgres_url:
        return []
    return [pg_list_tables, pg_describe_table, pg_read_query]
