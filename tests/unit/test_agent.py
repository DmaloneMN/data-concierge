"""Unit tests for the core agent."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.agent_config import AgentConfig
from src.agents.core_agent import CoreAgent


def _mock_response(
    *,
    content: str | None = None,
    finish_reason: str = "stop",
    tool_calls: list | None = None,
):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                finish_reason=finish_reason,
                message=SimpleNamespace(content=content, tool_calls=tool_calls or []),
            )
        ]
    )


@pytest.mark.asyncio
async def test_core_agent_run_stop():
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_mock_response(content="Done", finish_reason="stop")
    )

    with (
        patch("src.agents.core_agent.AsyncAzureOpenAI", return_value=mock_client),
        patch("src.agents.core_agent.load_prompt", return_value="system"),
    ):
        agent = CoreAgent(AgentConfig(max_iterations=2))
        result = await agent.run("hello")

    assert result == {"answer": "Done", "sql": None, "results": None}


@pytest.mark.asyncio
async def test_core_agent_run_tool_call():
    tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(
            name="get_table_schema",
            arguments=json.dumps({"table_name": "sales_fact"}),
        ),
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            _mock_response(finish_reason="tool_calls", tool_calls=[tool_call]),
            _mock_response(content="Here are the results", finish_reason="stop"),
        ]
    )
    mock_tool = MagicMock(
        return_value={
            "table_name": "sales_fact",
            "schema": "sales",
            "description": "Sales transactions fact table",
            "primary_key": "sale_id",
        }
    )

    with (
        patch("src.agents.core_agent.AsyncAzureOpenAI", return_value=mock_client),
        patch("src.agents.core_agent.load_prompt", return_value="system"),
        patch.dict("src.agents.core_agent.TOOL_CALLABLES", {"get_table_schema": mock_tool}),
    ):
        agent = CoreAgent(AgentConfig(max_iterations=2))
        result = await agent.run("describe sales_fact")

    assert result["answer"] == "Here are the results"
    mock_tool.assert_called_once_with(table_name="sales_fact")
    second_call_messages = mock_client.chat.completions.create.await_args_list[1].kwargs["messages"]
    assert any(
        isinstance(message, dict)
        and message.get("role") == "tool"
        and "table_name: sales_fact" in message.get("content", "")
        for message in second_call_messages
    )


@pytest.mark.asyncio
async def test_core_agent_max_iterations():
    tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(
            name="get_table_schema",
            arguments=json.dumps({"table_name": "sales_fact"}),
        ),
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=[
            _mock_response(finish_reason="tool_calls", tool_calls=[tool_call]),
            _mock_response(finish_reason="tool_calls", tool_calls=[tool_call]),
        ]
    )
    mock_tool = MagicMock(return_value={"table_name": "sales_fact"})

    with (
        patch("src.agents.core_agent.AsyncAzureOpenAI", return_value=mock_client),
        patch("src.agents.core_agent.load_prompt", return_value="system"),
        patch.dict("src.agents.core_agent.TOOL_CALLABLES", {"get_table_schema": mock_tool}),
    ):
        agent = CoreAgent(AgentConfig(max_iterations=2))
        result = await agent.run("describe sales_fact")

    assert (
        result["answer"]
        == "I was unable to fully answer your question. Please try rephrasing."
    )
