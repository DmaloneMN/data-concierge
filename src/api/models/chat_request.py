"""Chat request model."""
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str
    # TODO: Add conversation history, session_id, etc.
