"""Chat response model."""
from typing import Any

from pydantic import BaseModel


class ChatResponse(BaseModel):
    message: str
    sql: str | None = None
    results: dict[str, Any] | None = None
    # TODO: Add metadata, trace_id, etc.
