"""FastAPI entry point for the Data Concierge API."""
from fastapi import FastAPI
from src.api.routers import chat, health

app = FastAPI(title="Data Concierge API", version="0.1.0")

app.include_router(health.router)
app.include_router(chat.router, prefix="/chat")
