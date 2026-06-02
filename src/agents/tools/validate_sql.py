"""Tool: Validate SQL — uses LLM to review SQL for correctness and safety."""

from openai import AsyncAzureOpenAI

from src.shared.config import config
from src.shared.logging import get_logger
from src.shared.utils import load_prompt

logger = get_logger(__name__)

PROMPT_PATH = "src/agents/prompts/tools/validator_prompt.txt"

_client: AsyncAzureOpenAI | None = None


def _get_client() -> AsyncAzureOpenAI:
    global _client
    if _client is None:
        _client = AsyncAzureOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
        )
    return _client


async def validate_sql(sql: str, user_intent: str = "") -> dict:
    system_prompt = load_prompt(PROMPT_PATH)
    user_message = f"User intent: {user_intent}\n\nSQL to validate:\n{sql}"
    client = _get_client()
    response = await client.chat.completions.create(
        model=config.MODEL_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
        max_tokens=200,
    )
    result_text = (response.choices[0].message.content or "").strip()
    is_valid = result_text.upper().startswith("VALID")
    logger.info("SQL validation result: %s", result_text)
    return {"valid": is_valid, "reason": result_text}
