"""FastAPI entry point for the Data Concierge API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import chat, health
from src.shared.config import config
from src.shared.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Data Concierge API [%s]", config.ENVIRONMENT)
    config.validate()
    yield
    logger.info("Shutting down Data Concierge API")


app = FastAPI(
    title="Data Concierge API",
    version="0.1.0",
    description="Agentic data assistant powered by Azure AI Foundry and Microsoft Fabric.",
    lifespan=lifespan,
)

app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
