"""Unit tests for agent tools."""

import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.tools.execute_sql import _execute_sql_sync
from src.agents.tools.generate_sql import generate_sql
from src.agents.tools.get_table_schema import get_table_schema
from src.agents.tools.search_metric_definition import search_metric_definition
from src.agents.tools.create_ticket import create_ticket
from src.agents.tools.validate_sql import validate_sql
from src.shared.config import config


def _mock_openai_response(content: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ]
    )


def test_get_table_schema_found(tmp_path, monkeypatch):
    metadata = tmp_path / "tables.csv"
    metadata.write_text(
        "table_name,schema,description,primary_key\n"
        "sales_fact,sales,Sales transactions fact table,sale_id\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.agents.tools.get_table_schema.METADATA_PATH",
        str(metadata),
    )

    result = get_table_schema("sales_fact")

    assert result == {
        "table_name": "sales_fact",
        "schema": "sales",
        "description": "Sales transactions fact table",
        "primary_key": "sale_id",
    }


def test_get_table_schema_not_found(tmp_path, monkeypatch):
    metadata = tmp_path / "tables.csv"
    metadata.write_text(
        "table_name,schema,description,primary_key\n"
        "sales_fact,sales,Sales transactions fact table,sale_id\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.agents.tools.get_table_schema.METADATA_PATH",
        str(metadata),
    )

    with pytest.raises(ValueError, match="Table 'missing_table' not found"):
        get_table_schema("missing_table")


def test_get_table_schema_missing_file(tmp_path, monkeypatch):
    missing_path = tmp_path / "missing.csv"
    monkeypatch.setattr(
        "src.agents.tools.get_table_schema.METADATA_PATH",
        str(missing_path),
    )

    with pytest.raises(FileNotFoundError, match="Metadata file not found"):
        get_table_schema("sales_fact")


def test_search_metric_definition_found(tmp_path, monkeypatch):
    metadata = tmp_path / "metrics.csv"
    metadata.write_text(
        "metric_name,description,formula,source_table\n"
        "total_revenue,Total revenue from sales,SUM(sale_amount),sales_fact\n"
        "customer_count,Total unique customers,COUNT(DISTINCT customer_id),customer_dim\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.agents.tools.search_metric_definition.METRICS_PATH",
        str(metadata),
    )

    result = search_metric_definition("revenue")

    assert result == [
        {
            "metric_name": "total_revenue",
            "description": "Total revenue from sales",
            "formula": "SUM(sale_amount)",
            "source_table": "sales_fact",
        }
    ]


def test_search_metric_definition_no_match(tmp_path, monkeypatch):
    metadata = tmp_path / "metrics.csv"
    metadata.write_text(
        "metric_name,description,formula,source_table\n"
        "total_revenue,Total revenue from sales,SUM(sale_amount),sales_fact\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.agents.tools.search_metric_definition.METRICS_PATH",
        str(metadata),
    )

    assert search_metric_definition("margin") == []


def test_create_ticket_returns_stub():
    with (
        patch("src.agents.tools.create_ticket.ADO_ORG_URL", ""),
        patch("src.agents.tools.create_ticket.ADO_PROJECT", ""),
        patch("src.agents.tools.create_ticket.ADO_PAT", ""),
    ):
        result = create_ticket("Broken dashboard", "Revenue metric is wrong.")

    assert result["ticket_id"].startswith("STUB-")
    assert result["status"] == "created"
    assert result["title"] == "Broken dashboard"
    assert result["source"] == "stub"


def test_create_ticket_ado_success():
    """create_ticket calls ADO API when credentials are configured."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 42,
        "_links": {"html": {"href": "https://dev.azure.com/org/proj/_workitems/edit/42"}},
    }
    mock_response.raise_for_status = MagicMock()

    with (
        patch("src.agents.tools.create_ticket.ADO_ORG_URL", "https://dev.azure.com/org"),
        patch("src.agents.tools.create_ticket.ADO_PROJECT", "Proj"),
        patch("src.agents.tools.create_ticket.ADO_PAT", "token"),
        patch("httpx.patch", return_value=mock_response),
    ):
        from src.agents.tools.create_ticket import _create_ado_ticket

        result = _create_ado_ticket("Test bug", "Something broke")

    assert result["ticket_id"] == "42"
    assert result["source"] == "azure_devops"
    assert "url" in result


def test_create_ticket_ado_fallback_to_stub():
    """create_ticket falls back to stub when ADO env vars are missing."""
    with (
        patch("src.agents.tools.create_ticket.ADO_ORG_URL", ""),
        patch("src.agents.tools.create_ticket.ADO_PROJECT", ""),
        patch("src.agents.tools.create_ticket.ADO_PAT", ""),
    ):
        result = create_ticket("Test", "Description")

    assert result["source"] == "stub"
    assert result["ticket_id"].startswith("STUB-")


@pytest.mark.asyncio
async def test_validate_sql_valid():
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(
                    return_value=_mock_openai_response("VALID Safe read-only query")
                )
            )
        )
    )

    with (
        patch("src.agents.tools.validate_sql._get_client", return_value=mock_client),
        patch("src.agents.tools.validate_sql.load_prompt", return_value="prompt"),
    ):
        result = await validate_sql("SELECT * FROM sales.sales_fact", "Show revenue")

    assert result == {
        "valid": True,
        "reason": "VALID Safe read-only query",
    }
    create_call = mock_client.chat.completions.create.await_args
    assert any(
        "User intent: Show revenue" in message["content"]
        for message in create_call.kwargs["messages"]
        if isinstance(message, dict) and "content" in message
    )


@pytest.mark.asyncio
async def test_validate_sql_invalid():
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(
                    return_value=_mock_openai_response("INVALID Destructive statement")
                )
            )
        )
    )

    with (
        patch("src.agents.tools.validate_sql._get_client", return_value=mock_client),
        patch("src.agents.tools.validate_sql.load_prompt", return_value="prompt"),
    ):
        result = await validate_sql("DELETE FROM sales.sales_fact")

    assert result == {
        "valid": False,
        "reason": "INVALID Destructive statement",
    }


@pytest.mark.asyncio
async def test_generate_sql_returns_string():
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=AsyncMock(
                    return_value=_mock_openai_response(
                        "SELECT TOP 1 * FROM sales.sales_fact"
                    )
                )
            )
        )
    )

    with (
        patch("src.agents.tools.generate_sql._get_client", return_value=mock_client),
        patch("src.agents.tools.generate_sql.load_prompt", return_value="prompt"),
    ):
        result = await generate_sql("Show one row", "schema: sales_fact")

    assert result == "SELECT TOP 1 * FROM sales.sales_fact"


def test_execute_sql_missing_config(monkeypatch):
    monkeypatch.setattr(config, "FABRIC_SQL_ENDPOINT", "")
    monkeypatch.setattr(config, "FABRIC_DATABASE", "")

    with pytest.raises(EnvironmentError, match="FABRIC_SQL_ENDPOINT and FABRIC_DATABASE"):
        _execute_sql_sync("SELECT 1")


def test_execute_sql_truncates_results(monkeypatch):
    cursor = MagicMock()
    cursor.description = [("id",), ("name",)]
    cursor.execute.return_value = None
    cursor.fetchmany.return_value = [(1, "a"), (2, "b"), (3, "c")]

    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = None
    connection.cursor.return_value = cursor

    pyodbc = MagicMock()
    pyodbc.connect.return_value = connection

    monkeypatch.setattr(config, "FABRIC_SQL_ENDPOINT", "endpoint")
    monkeypatch.setattr(config, "FABRIC_DATABASE", "database")
    monkeypatch.setattr("src.agents.tools.execute_sql.MAX_ROWS", 2)
    monkeypatch.setattr("src.agents.tools.execute_sql._get_token", lambda: b"token")
    monkeypatch.setitem(sys.modules, "pyodbc", pyodbc)

    result = _execute_sql_sync("SELECT id, name FROM sales.sales_fact")

    assert result == {
        "columns": ["id", "name"],
        "rows": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}],
        "row_count": 2,
        "truncated": True,
        "max_rows": 2,
    }
