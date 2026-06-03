"""Integration test for execute_sql against a real Fabric SQL endpoint.

Skipped automatically if FABRIC_SQL_ENDPOINT is not configured.
Run locally after setting FABRIC_SQL_ENDPOINT and FABRIC_DATABASE in .env.

    pytest tests/integration/ -v
"""

import importlib
import os

import pytest

FABRIC_CONFIGURED = bool(os.getenv("FABRIC_SQL_ENDPOINT"))
skip_no_fabric = pytest.mark.skipif(
    not FABRIC_CONFIGURED, reason="FABRIC_SQL_ENDPOINT not configured — skipping live Fabric tests"
)


@skip_no_fabric
@pytest.mark.asyncio
async def test_execute_sql_live_simple_query():
    """Execute a simple SELECT 1 query against the Fabric endpoint."""
    from src.agents.tools.execute_sql import execute_sql

    result = await execute_sql("SELECT 1 AS test_value")
    assert "rows" in result
    assert "columns" in result
    assert result["row_count"] >= 0


@skip_no_fabric
@pytest.mark.asyncio
async def test_execute_sql_live_sales_fact():
    """Query the top 5 rows from sales_fact."""
    from src.agents.tools.execute_sql import execute_sql

    result = await execute_sql("SELECT TOP 5 * FROM sales.sales_fact")
    assert "rows" in result
    assert isinstance(result["rows"], list)


@skip_no_fabric
@pytest.mark.asyncio
async def test_execute_sql_live_respects_max_rows(monkeypatch):
    """Verify MAX_ROWS cap is respected."""
    import src.agents.tools.execute_sql as module

    monkeypatch.setattr(module, "MAX_ROWS", 2)
    importlib.reload(module)

    result = await module.execute_sql("SELECT * FROM sales.sales_fact")
    assert result["row_count"] <= 2
