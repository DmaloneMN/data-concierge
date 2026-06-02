"""Tool: Execute SQL — runs a validated SQL query against the Fabric SQL Analytics Endpoint."""

import asyncio
import os
import struct

from azure.identity import DefaultAzureCredential

from src.shared.config import config
from src.shared.logging import get_logger

logger = get_logger(__name__)

SQL_COPT_SS_ACCESS_TOKEN = 1256
MAX_ROWS = int(os.getenv("EXECUTE_SQL_MAX_ROWS", "500"))


def _get_token() -> bytes:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode("UTF-16-LE")
    return struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)


def _execute_sql_sync(sql: str) -> dict:
    if not config.FABRIC_SQL_ENDPOINT or not config.FABRIC_DATABASE:
        raise EnvironmentError(
            "FABRIC_SQL_ENDPOINT and FABRIC_DATABASE must be set to execute SQL."
        )

    try:
        import pyodbc  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "pyodbc is required for execute_sql. Install it with: pip install pyodbc"
        ) from exc

    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={config.FABRIC_SQL_ENDPOINT},1433;"
        f"Database={config.FABRIC_DATABASE};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

    token_struct = _get_token()
    logger.info("Executing SQL against Fabric: %s", sql[:200])

    with pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)

        if cursor.description is None:
            logger.info("execute_sql returned no result set")
            return {"columns": [], "rows": [], "row_count": 0}

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchmany(MAX_ROWS)
        results = [dict(zip(columns, row)) for row in rows]

    logger.info("execute_sql returned %d rows", len(results))
    return {"columns": columns, "rows": results, "row_count": len(results)}


async def execute_sql(sql: str) -> dict:
    return await asyncio.to_thread(_execute_sql_sync, sql)
