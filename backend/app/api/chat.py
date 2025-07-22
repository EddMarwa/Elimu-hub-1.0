from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.config import settings
from app.utils.logger import logger
from starlette.concurrency import run_in_threadpool
from typing import List, Optional
import time
import json

router = APIRouter()

# --- Test LLM Endpoint (for debugging) ---
@router.get("/test-llm")
async def test_llm():
    """Test endpoint to verify LLM service works"""
    try:
        llm = LLMService(provider="openrouter")
        response = llm.call_llm("What is 2+2? Answer briefly.")
        return {
            "status": "success", 
            "provider": llm.provider,
            "model": llm.model,
            "api_key_configured": bool(llm.api_key),
            "response": response
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# --- List Topics Endpoint ---
@router.get("/list-topics")
def list_topics():
    # Replace with DB query if you have a Topic model
    return {"topics": [
        {"id": 1, "name": "Mathematics"},
        {"id": 2, "name": "Science"},
        {"id": 3, "name": "English"},
        {"id": 4, "name": "History"},
        {"id": 5, "name": "Kiswahili"}
    ]}

# --- OpenAI-compatible LLM Chat Completions Endpoint ---
@router.post("/llm/chat/completions")
async def llm_chat_completions(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    prompt = ""
    for msg in messages:
        if msg["role"] == "user":
            prompt += msg["content"] + "\n"
    llm = LLMService()
    answer = llm.call_llm(prompt)
    return JSONResponse(content={
        "choices": [{"message": {"content": answer}}],
        "usage": {"total_tokens": len(prompt.split())}
    })

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    topic: str = Field(..., min_length=1, max_length=100, description="The topic to search in")
    session_id: Optional[int] = Field(None, description="Chat session ID (optional)")

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    used_context: List[str]
    llm: str
    confidence: Optional[float] = None
    session_id: Optional[int] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    start_time = time.time()
    logger.info(f"Chat request - Topic: {req.topic}, Question: {req.question[:50]}...")
    
    try:
        # Validate inputs
        if not req.question.strip():
            logger.warning("Empty question received")
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        if not req.topic.strip():
            logger.warning("Empty topic received")
            raise HTTPException(status_code=400, detail="Topic cannot be empty")

        # Initialize LLM service with OpenRouter
        llm = LLMService(provider="openrouter")
        logger.info(f"Initialized LLM service with provider: {llm.provider}, model: {llm.model}")
        
        # Call LLM directly for response (no authentication required)
        logger.info("Calling LLM service directly for response")
        answer = llm.call_llm_with_context(req.question, context_documents=None)
        
        logger.info(f"LLM response received: {answer[:100]}...")
        
        # Check if LLM response contains error
        if answer.startswith("[LLM ERROR]") or answer.startswith("[ERROR]"):
            logger.error(f"LLM service error: {answer}")
            return JSONResponse(content={
                "status": "error",
                "message": f"LLM service error: {answer}"
            })

        process_time = time.time() - start_time
        logger.info(f"Chat response generated successfully in {process_time:.3f}s")
        
        return ChatResponse(
            answer=answer,
            sources=[],
            used_context=[],
            llm=llm.model,
            confidence=1.0,
            session_id=None  # No session tracking without authentication
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing chat request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return JSONResponse(content={
            "status": "error",
            "message": f"Chat error: {str(e)}"  # Show actual error for debugging
        }) 