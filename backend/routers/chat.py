from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.chat_service import get_chat_response

router = APIRouter()

class Message(BaseModel):
    role: str    # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]  # full conversation history

@router.post("/message")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        reply = get_chat_response(messages)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
