"""Agent configuration — loaded from shared Config."""

import os
from dataclasses import dataclass

from src.shared.config import config


@dataclass
class AgentConfig:
    model_deployment: str = config.MODEL_DEPLOYMENT
    azure_openai_endpoint: str = config.AZURE_OPENAI_ENDPOINT
    azure_openai_api_key: str = config.AZURE_OPENAI_API_KEY
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "8"))
    temperature: float = float(os.getenv("AGENT_TEMPERATURE", "0.0"))
    system_prompt_path: str = "src/agents/prompts/system/core_agent_system.txt"
