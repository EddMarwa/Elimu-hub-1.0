from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chat_service import ChatService

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    topic: str

@router.post("/chat")
def chat(req: ChatRequest):
    chat_service = ChatService()
    answer = chat_service.answer(req.topic, req.question)
    return {"answer": answer} 