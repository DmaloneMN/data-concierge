"""Health check router."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
asynchronous def health():
    return {"status": "ok"}
