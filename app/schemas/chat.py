from pydantic import BaseModel
from typing import Optional, List


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    scan_context: Optional[dict] = None
    history: List[ChatMessage] = []

