from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest
from app.services.chat_service import ask_gemini

router = APIRouter()

@router.post("/")
async def chat(req: ChatRequest):
    try:
        return {"reply": await ask_gemini(req)}
    except Exception as e:
        raise HTTPException(500, str(e))