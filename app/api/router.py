from fastapi import APIRouter
from app.api.routes import patients, analyze, chat, health

api_router = APIRouter()

api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, tags=["health"])