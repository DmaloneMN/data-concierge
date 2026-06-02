"""Core AI agent orchestration loop (local runnable MVP).

Uses Azure OpenAI function-calling to orchestrate tools.
"""

import asyncio
import inspect
import json

from openai import AsyncAzureOpenAI

from src.agents.agent_config import AgentConfig
from src.agents.tools.tool_registry import TOOL_CALLABLES, TOOLS
from src.shared.logging import get_logger
from src.shared.utils import format_schema_context, load_prompt

logger = get_logger(__name__)


class CoreAgent:
    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig()
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.config.azure_openai_endpoint,
            api_key=self.config.azure_openai_api_key,
            api_version="2024-02-01",
        )
        self.system_prompt = load_prompt(self.config.system_prompt_path)

    async def run(self, message: str) -> dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message},
        ]

        sql_generated: str | None = None
        results_data: dict | None = None

        for _ in range(self.config.max_iterations):
            response = await self.client.chat.completions.create(
                model=self.config.model_deployment,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=self.config.temperature,
            )

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    if tool_name not in TOOL_CALLABLES:
                        tool_result = f"Error: unknown tool '{tool_name}'"
                    else:
                        fn = TOOL_CALLABLES[tool_name]
                        try:
                            if inspect.iscoroutinefunction(fn):
                                tool_result = await fn(**tool_args)
                            else:
                                tool_result = await asyncio.to_thread(fn, **tool_args)
                        except Exception as exc:
                            logger.exception("Tool '%s' failed", tool_name)
                            tool_result = f"Error running tool '{tool_name}': {exc}"

                        if tool_name == "generate_sql":
                            sql_generated = tool_result
                        if tool_name == "execute_sql":
                            results_data = tool_result

                    tool_content = str(tool_result)
                    if tool_name == "get_table_schema" and isinstance(tool_result, dict):
                        tool_content = format_schema_context(tool_result)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_content,
                        }
                    )

            elif choice.finish_reason == "stop":
                return {
                    "answer": choice.message.content,
                    "sql": sql_generated,
                    "results": results_data,
                }

            else:
                logger.warning("Unexpected finish_reason: %s", choice.finish_reason)
                break

        return {
            "answer": "I was unable to fully answer your question. Please try rephrasing.",
            "sql": sql_generated,
            "results": results_data,
        }
