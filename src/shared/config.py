"""Shared configuration loaded from environment variables / Key Vault."
import os

class Config:
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    MODEL_DEPLOYMENT: str = os.getenv("MODEL_DEPLOYMENT", "gpt-4o")
    # TODO: Add remaining config fields
