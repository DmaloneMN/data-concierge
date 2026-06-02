"""Tool: Generate SQL.

Uses Azure OpenAI to generate SQL using the sql_generator_prompt.txt.
"""

from openai import AsyncAzureOpenAI

from src.shared.config import config
from src.shared.logging import get_logger
from src.shared.utils import load_prompt, truncate_text

logger = get_logger(__name__)

PROMPT_PATH = "src/agents/prompts/tools/sql_generator_prompt.txt"

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


async def generate_sql(question: str, schema_context: str) -> str:
    system_prompt = load_prompt(PROMPT_PATH)
    schema_context = truncate_text(schema_context, max_tokens=2000)

    user_message = f"Table schema context:\n{schema_context}\n\nUser question: {question}"

    client = _get_client()
    response = await client.chat.completions.create(
        model=config.MODEL_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
        max_tokens=500,
    )

    sql = (response.choices[0].message.content or "").strip()
    logger.info("Generated SQL: %s", sql)
    return sql
