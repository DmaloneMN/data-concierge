"""Chat router - handles user query requests."""
from fastapi import APIRouter, Depends
from src.api.models.chat_request import ChatRequest
from src.api.models.chat_response import ChatResponse

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # TODO: Invoke core agent
    raise NotImplementedError
