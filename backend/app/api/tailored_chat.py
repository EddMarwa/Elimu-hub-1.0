"""
Enhanced Chat API with Response Tailoring
Provides advanced customization options for LLM responses
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import time
import json

from app.services.enhanced_llm_service import (
    EnhancedLLMService, 
    ResponseTone, 
    ResponseFormat, 
    AudienceLevel,
    create_student_tutor_response,
    create_professional_summary,
    create_step_by_step_guide
)
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.utils.logger import logger

router = APIRouter()

# Pydantic models for request/response
class TailoredChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    topic: str = Field(..., min_length=1, max_length=100, description="The topic to search in")
    
    # Response customization options
    tone: Optional[str] = Field("friendly", description="Response tone: professional, friendly, academic, conversational, encouraging, detailed, concise")
    format_type: Optional[str] = Field("paragraph", description="Response format: paragraph, bullet_points, numbered_list, q_and_a, step_by_step, summary, explanation")
    audience_level: Optional[str] = Field("high_school", description="Target audience: elementary, middle_school, high_school, college, adult, expert")
    
    # Additional customization
    custom_instructions: Optional[str] = Field(None, max_length=500, description="Additional instructions for the response")
    persona: Optional[str] = Field(None, max_length=200, description="Custom persona for the AI assistant")
    
    # Technical parameters
    max_tokens: Optional[int] = Field(512, ge=50, le=2048, description="Maximum response length")
    temperature: Optional[float] = Field(0.7, ge=0.1, le=2.0, description="Response creativity level")
    
    # RAG options
    use_context: Optional[bool] = Field(True, description="Whether to use document context")
    session_id: Optional[int] = Field(None, description="Chat session ID (optional)")

class TailoredChatResponse(BaseModel):
    answer: str
    sources: List[str]
    used_context: List[str]
    llm_model: str
    response_config: Dict[str, Any]
    confidence: Optional[float] = None
    session_id: Optional[int] = None
    processing_time: float

class QuickResponseRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    subject: str = Field(..., min_length=1, max_length=100)
    response_type: str = Field(..., description="student_tutor, professional_summary, or step_by_step")
    grade_level: Optional[str] = Field("high_school", description="For student_tutor type only")

@router.post("/chat/tailored", response_model=TailoredChatResponse)
async def tailored_chat(req: TailoredChatRequest):
    """
    Advanced chat endpoint with full response customization options
    """
    start_time = time.time()
    logger.info(f"Tailored chat request - Topic: {req.topic}, Tone: {req.tone}, Format: {req.format_type}")
    
    try:
        # Validate inputs
        if not req.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Validate enum values
        try:
            tone = ResponseTone(req.tone.lower())
            format_type = ResponseFormat(req.format_type.lower())
            audience_level = AudienceLevel(req.audience_level.lower())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
        
        # Initialize enhanced LLM service
        llm = EnhancedLLMService(provider="groq")
        logger.info(f"Initialized enhanced LLM service with provider: {llm.provider}")
        
        # Retrieve context documents if requested
        context_documents = []
        sources = []
        used_context = []
        
        if req.use_context:
            try:
                logger.info(f"Searching for relevant context for topic: {req.topic}")
                vector_store = VectorStore()
                embedding_service = EmbeddingService()
                
                # Generate embedding for the question
                query_embedding = embedding_service.generate_embedding(req.question)
                
                # Search for relevant document chunks
                context_documents = vector_store.search_similar(
                    query_embedding, 
                    topic_filter=req.topic,
                    top_k=3
                )
                
                logger.info(f"Found {len(context_documents)} relevant document chunks")
                
                # Extract sources and context
                if context_documents:
                    for doc in context_documents:
                        if doc.get('source'):
                            sources.append(doc['source'])
                        if doc.get('content'):
                            used_context.append(doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'])
                            
            except Exception as search_error:
                logger.warning(f"Vector search failed: {search_error}")
                context_documents = []
        
        # Generate tailored response
        answer = llm.call_llm_tailored(
            prompt=req.question,
            tone=tone,
            format_type=format_type,
            audience_level=audience_level,
            subject_area=req.topic,
            custom_instructions=req.custom_instructions,
            persona=req.persona,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            context_documents=context_documents if req.use_context else None
        )
        
        logger.info(f"Tailored LLM response received: {answer[:100]}...")
        
        # Check for errors
        if answer.startswith("[LLM ERROR]") or answer.startswith("[ERROR]"):
            logger.error(f"LLM service error: {answer}")
            raise HTTPException(status_code=500, detail=f"LLM service error: {answer}")
        
        processing_time = time.time() - start_time
        logger.info(f"Tailored chat response generated successfully in {processing_time:.3f}s")
        
        # Response configuration details
        response_config = {
            "tone": req.tone,
            "format": req.format_type,
            "audience_level": req.audience_level,
            "subject_area": req.topic,
            "custom_instructions": req.custom_instructions,
            "persona": req.persona,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "used_context": req.use_context,
            "provider": llm.provider
        }
        
        return TailoredChatResponse(
            answer=answer,
            sources=sources,
            used_context=used_context,
            llm_model=llm.model,
            response_config=response_config,
            confidence=0.95,  # Could be calculated based on context relevance
            session_id=req.session_id,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing tailored chat request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/chat/quick")
async def quick_response(req: QuickResponseRequest):
    """
    Quick response endpoint with predefined response styles
    """
    start_time = time.time()
    logger.info(f"Quick response request - Type: {req.response_type}, Subject: {req.subject}")
    
    try:
        if req.response_type == "student_tutor":
            answer = create_student_tutor_response(req.question, req.subject, req.grade_level)
        elif req.response_type == "professional_summary":
            answer = create_professional_summary(req.question, req.subject)
        elif req.response_type == "step_by_step":
            answer = create_step_by_step_guide(req.question, req.subject)
        else:
            raise HTTPException(status_code=400, detail="Invalid response_type. Use: student_tutor, professional_summary, or step_by_step")
        
        processing_time = time.time() - start_time
        
        return {
            "answer": answer,
            "response_type": req.response_type,
            "subject": req.subject,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error in quick response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.get("/chat/response-options")
async def get_response_options():
    """
    Get available response customization options
    """
    return {
        "tones": [tone.value for tone in ResponseTone],
        "formats": [fmt.value for fmt in ResponseFormat],
        "audience_levels": [level.value for level in AudienceLevel],
        "quick_response_types": ["student_tutor", "professional_summary", "step_by_step"],
        "grade_levels": ["elementary", "middle_school", "high_school", "college"],
        "default_values": {
            "tone": "friendly",
            "format_type": "paragraph",
            "audience_level": "high_school",
            "max_tokens": 512,
            "temperature": 0.7,
            "use_context": True
        }
    }

# Example usage endpoint for testing
@router.post("/chat/examples")
async def get_response_examples():
    """
    Show examples of different response styles for the same question
    """
    sample_question = "Explain photosynthesis"
    subject = "Biology"
    
    llm = EnhancedLLMService(provider="groq")
    
    examples = {}
    
    # Different tones
    examples["tones"] = {}
    for tone in [ResponseTone.ACADEMIC, ResponseTone.FRIENDLY, ResponseTone.CONCISE]:
        response = llm.call_llm_tailored(
            prompt=sample_question,
            tone=tone,
            subject_area=subject,
            max_tokens=200
        )
        examples["tones"][tone.value] = response[:150] + "..." if len(response) > 150 else response
    
    # Different formats
    examples["formats"] = {}
    for fmt in [ResponseFormat.BULLET_POINTS, ResponseFormat.STEP_BY_STEP, ResponseFormat.SUMMARY]:
        response = llm.call_llm_tailored(
            prompt=sample_question,
            format_type=fmt,
            subject_area=subject,
            max_tokens=200
        )
        examples["formats"][fmt.value] = response[:150] + "..." if len(response) > 150 else response
    
    return {
        "question": sample_question,
        "subject": subject,
        "examples": examples,
        "note": "These are shortened examples. Full responses would be longer and more detailed."
    }
