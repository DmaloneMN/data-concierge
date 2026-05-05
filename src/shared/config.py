"""Shared configuration loaded from environment variables / Key Vault."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    MODEL_DEPLOYMENT: str = os.getenv("MODEL_DEPLOYMENT", "gpt-4o")

    # Fabric
    FABRIC_SQL_ENDPOINT: str = os.getenv("FABRIC_SQL_ENDPOINT", "")
    FABRIC_DATABASE: str = os.getenv("FABRIC_DATABASE", "")

    # Key Vault (optional for local dev)
    KEY_VAULT_URL: str = os.getenv("KEY_VAULT_URL", "")

    # App
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "dev")

    def validate(self) -> None:
        """Validate required configuration for local runtime."""
        missing = []
        if not self.AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.AZURE_OPENAI_API_KEY:
            missing.append("AZURE_OPENAI_API_KEY")
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in your values."
            )


config = Config()
