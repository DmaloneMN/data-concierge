"""Chat router — handles user query requests."""

from fastapi import APIRouter, HTTPException

from src.agents.agent_config import AgentConfig
from src.agents.core_agent import CoreAgent
from src.api.models.chat_request import ChatRequest
from src.api.models.chat_response import ChatResponse
from src.shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

_agent = CoreAgent(AgentConfig())


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await _agent.run(request.message)
        return ChatResponse(message=result["answer"], sql=result.get("sql"))
    except Exception as e:
        logger.exception("Chat failed: %s", e)
        raise HTTPException(status_code=500, detail="Agent encountered an error.")
