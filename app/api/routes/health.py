from fastapi import APIRouter
from app.ai.model import MODEL_LOADED
from app.services.chat_service import GEMINI_API_KEY

router = APIRouter()


@router.get("/")
def health():
    return {
        "status": "ok",
        "model_loaded": MODEL_LOADED,
        "gemini_configured": bool(GEMINI_API_KEY)
    }