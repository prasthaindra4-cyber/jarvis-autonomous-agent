from fastapi import APIRouter
from app.core.config import settings
from app.core.llm_provider import llm_provider

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_live_mode": llm_provider.is_live,
        "primary_model": settings.GEMINI_MODEL
    }
