from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user, get_current_admin_user
from app.auth.models import User
from app.services.llm_service import LLMService
from app.utils.logger import logger
from starlette.concurrency import run_in_threadpool
from typing import List, Optional, Dict, Any
import time
import json

router = APIRouter()

class CompletionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000, description="The prompt to complete")
    max_tokens: int = Field(512, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.1, le=2.0, description="Temperature for randomness")
    stream: bool = Field(False, description="Whether to stream the response")
    model: Optional[str] = Field(None, description="Model to use (optional)")

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="List of messages")
    max_tokens: int = Field(512, ge=1, le=2048)
    temperature: float = Field(0.7, ge=0.1, le=2.0)
    stream: bool = Field(False)
    model: Optional[str] = Field(None)

class GenerativeResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    processing_time: float
    confidence: Optional[float] = None

@router.post("/llm/completions", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate text completion using the local LLM."""
    start_time = time.time()
    
    try:
        llm = LLMService()
        
        # Generate completion
        logger.info(f"User {current_user.email} requesting completion")
        response_text = await run_in_threadpool(
            llm.call_llm, 
            request.prompt, 
            request.max_tokens, 
            request.temperature
        )
        
        processing_time = time.time() - start_time
        
        # Calculate token usage (approximate)
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(response_text.split())
        total_tokens = prompt_tokens + completion_tokens
        
        logger.info(f"Completion generated in {processing_time:.3f}s - {total_tokens} tokens")
        
        return CompletionResponse(
            id=f"cmpl-{int(time.time())}",
            created=int(time.time()),
            model=llm.llm_name,
            choices=[{
                "text": response_text,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating completion for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")

@router.post("/llm/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate chat completion using the local LLM."""
    start_time = time.time()
    
    try:
        llm = LLMService()
        
        # Convert messages to prompt
        prompt_parts = []
        for message in request.messages:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"User: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")
        
        prompt_parts.append("Assistant:")
        prompt = "\n".join(prompt_parts)
        
        logger.info(f"User {current_user.email} requesting chat completion")
        response_text = await run_in_threadpool(
            llm.call_llm, 
            prompt, 
            request.max_tokens, 
            request.temperature
        )
        
        processing_time = time.time() - start_time
        
        # Calculate token usage
        prompt_tokens = len(prompt.split())
        completion_tokens = len(response_text.split())
        total_tokens = prompt_tokens + completion_tokens
        
        logger.info(f"Chat completion generated in {processing_time:.3f}s - {total_tokens} tokens")
        
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": llm.llm_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating chat completion for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating chat completion: {str(e)}")

@router.post("/llm/generate", response_model=GenerativeResponse)
async def generate_content(
    prompt: str = Form(...),
    max_tokens: int = Form(512),
    temperature: float = Form(0.7),
    current_user: User = Depends(get_current_active_user)
):
    """Simple generative AI endpoint for quick text generation."""
    start_time = time.time()
    
    try:
        llm = LLMService()
        
        logger.info(f"User {current_user.email} requesting content generation")
        response_text = await run_in_threadpool(
            llm.call_llm, 
            prompt, 
            max_tokens, 
            temperature
        )
        
        processing_time = time.time() - start_time
        tokens_used = len(prompt.split()) + len(response_text.split())
        
        logger.info(f"Content generated in {processing_time:.3f}s - {tokens_used} tokens")
        
        return GenerativeResponse(
            response=response_text,
            model=llm.llm_name,
            tokens_used=tokens_used,
            processing_time=processing_time,
            confidence=0.85  # Can be calculated based on model confidence
        )
        
    except Exception as e:
        logger.error(f"Error generating content for user {current_user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@router.get("/llm/models")
async def list_models(current_user: User = Depends(get_current_active_user)):
    """List available models."""
    llm = LLMService()
    return {
        "object": "list",
        "data": [{
            "id": llm.llm_name.lower().replace(" ", "-"),
            "object": "model",
            "created": int(time.time()),
            "owned_by": "elimu-hub",
            "permission": [],
            "root": llm.llm_name,
            "parent": None
        }]
    }

@router.get("/llm/health")
async def llm_health_check():
    """Health check for LLM service."""
    try:
        llm = LLMService()
        # Simple test prompt
        test_response = llm.call_llm("Say 'OK'", max_tokens=5, temp=0.1)
        
        return {
            "status": "healthy",
            "model": llm.llm_name,
            "model_path": llm.model_path,
            "test_response": test_response,
            "timestamp": int(time.time())
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": int(time.time())
        }
