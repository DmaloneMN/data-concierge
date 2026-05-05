"""Unit tests for FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("src.api.routers.chat._agent")
def test_chat_success(mock_agent):
    mock_agent.run = AsyncMock(
        return_value={
            "answer": "Total revenue was $1M.",
            "sql": "SELECT SUM(sale_amount) FROM sales_fact",
        }
    )
    response = client.post(
        "/chat/", json={"user_id": "user1", "message": "What was total revenue?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "sql" in data


@patch("src.api.routers.chat._agent")
def test_chat_agent_error(mock_agent):
    mock_agent.run = AsyncMock(side_effect=Exception("LLM error"))
    response = client.post(
        "/chat/", json={"user_id": "user1", "message": "What was revenue?"}
    )
    assert response.status_code == 500
