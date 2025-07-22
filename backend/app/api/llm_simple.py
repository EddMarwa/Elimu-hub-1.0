from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.llm_service import LLMService
from app.utils.logger import logger
from starlette.concurrency import run_in_threadpool
from typing import List, Optional, Dict, Any
import time
import json
import uuid

router = APIRouter()

class CompletionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=5000, description="The prompt to complete")
    max_tokens: int = Field(512, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(0.7, ge=0.1, le=2.0, description="Temperature for randomness")
    model: Optional[str] = Field(None, description="Model to use (optional)")

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

@router.post("/llm/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    """Generate text completion using the LLM."""
    start_time = time.time()
    
    try:
        llm = LLMService()
        
        # Generate completion
        logger.info("LLM completion requested")
        response_text = await run_in_threadpool(
            llm.call_llm, 
            request.prompt, 
            request.max_tokens,
            request.temperature
        )
        
        # Create OpenAI-compatible response
        completion_id = f"cmpl-{uuid.uuid4().hex[:12]}"
        created_timestamp = int(time.time())
        
        response = CompletionResponse(
            id=completion_id,
            object="text_completion",
            created=created_timestamp,
            model=llm.model,
            choices=[{
                "text": response_text,
                "index": 0,
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(request.prompt.split()) + len(response_text.split())
            }
        )
        
        process_time = time.time() - start_time
        logger.info(f"Completion generated successfully in {process_time:.3f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate completion: {str(e)}"
        )

@router.post("/llm/chat/completions")
async def create_chat_completion(request: dict):
    """Generate chat completion using the LLM."""
    start_time = time.time()
    
    try:
        llm = LLMService()
        
        # Extract messages from request
        messages = request.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")
        
        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Generate response
        logger.info("Chat completion requested")
        response_text = await run_in_threadpool(
            llm.call_llm, 
            user_message,
            request.get("max_tokens", 1024),
            request.get("temperature", 0.7)
        )
        
        # Create OpenAI-compatible response
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created_timestamp = int(time.time())
        
        response = {
            "id": completion_id,
            "object": "chat.completion",
            "created": created_timestamp,
            "model": llm.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_message.split()) + len(response_text.split())
            }
        }
        
        process_time = time.time() - start_time
        logger.info(f"Chat completion generated successfully in {process_time:.3f}s")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating chat completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate chat completion: {str(e)}"
        )

@router.get("/llm/models")
async def list_models():
    """List available LLM models."""
    try:
        # Return available models
        models = [
            {
                "id": "qwen/qwen-2.5-72b-instruct",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openrouter",
                "permission": [],
                "root": "qwen/qwen-2.5-72b-instruct",
                "parent": None
            },
            {
                "id": "mixtral-8x7b-32768", 
                "object": "model",
                "created": int(time.time()),
                "owned_by": "groq",
                "permission": [],
                "root": "mixtral-8x7b-32768",
                "parent": None
            }
        ]
        
        return {"object": "list", "data": models}
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list models"
        )
