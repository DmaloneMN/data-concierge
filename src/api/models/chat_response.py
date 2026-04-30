"""Chat response model."""
from pydantic import BaseModel

class ChatResponse(BaseModel):
    message: str
    sql: str | None = None
    # TODO: Add metadata, trace_id, etc.
