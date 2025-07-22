from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.models.chat import ChatSession, ChatMessage
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
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    logger.info(f"User {current_user.email} chat request - Topic: {req.topic}, Question: {req.question[:50]}...")
    
    try:
        # Validate inputs
        if not req.question.strip():
            logger.warning(f"User {current_user.email} sent empty question")
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        if not req.topic.strip():
            logger.warning(f"User {current_user.email} sent empty topic")
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        # Get or create chat session
        session = None
        if req.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == req.session_id,
                ChatSession.user_id == current_user.id,
                ChatSession.is_active == True
            ).first()
            
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found")
        else:
            # Create new session
            session = ChatSession(
                user_id=current_user.id,
                topic=req.topic,
                title=req.question[:50] + "..." if len(req.question) > 50 else req.question
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            logger.info(f"Created new chat session {session.id} for user {current_user.email}")
        
        # Initialize services
        embedder = EmbeddingService()
        vector_store = VectorStore()
        llm = LLMService(provider="openrouter")  # Use OpenRouter with Qwen
        
        # Generate embeddings
        logger.debug("Generating question embeddings")
        q_emb = await run_in_threadpool(embedder.embed_texts, [req.question])
        q_emb = q_emb[0]
        
        # Search for relevant documents
        logger.debug(f"Searching for relevant documents in topic: {req.topic}")
        results = await run_in_threadpool(
            vector_store.similarity_search, 
            req.topic, 
            q_emb, 
            settings.TOP_K_RESULTS
        )
        
        docs = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]
        
        logger.info(f"Found {len(docs)} relevant documents")
        
        # Check if we have relevant results
        if not docs or not metadatas or not distances:
            logger.warning(f"No documents found for topic: {req.topic}")
            # Use LLM without context
            answer = await run_in_threadpool(
                llm.call_llm_with_context, 
                req.question, 
                context_documents=None
            )
            sources = []
            used_context = []
            confidence = None
        elif distances[0] > settings.SIMILARITY_THRESHOLD:
            logger.warning(f"Best match distance ({distances[0]}) exceeds threshold ({settings.SIMILARITY_THRESHOLD})")
            # Use LLM without context
            answer = await run_in_threadpool(
                llm.call_llm_with_context, 
                req.question, 
                context_documents=None
            )
            sources = []
            used_context = []
            confidence = None
        else:
            # Prepare context documents
            context_documents = [
                {"content": doc, "metadata": meta} 
                for doc, meta in zip(docs, metadatas)
            ]
            sources = [f"{m.get('source_file','Unknown')}:page {m.get('page','?')}" for m in metadatas]
            
            # Get LLM response with context
            logger.debug("Generating LLM response with context")
            answer = await run_in_threadpool(
                llm.call_llm_with_context, 
                req.question, 
                context_documents=context_documents
            )
            
            # Calculate confidence based on distance
            confidence = 1.0 - distances[0] if distances else None
            used_context = docs
        
        # Fallback if LLM response is empty/null/undefined
        if not answer or not str(answer).strip():
            return JSONResponse(content={
                "status": "error",
                "message": f"I'm currently unable to answer your question about '{req.question}'. Please try again later."
            })

        # Save user message to chat history
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=req.question
        )
        db.add(user_message)
        
        # Save assistant response to chat history
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            confidence=confidence,
            sources=json.dumps(sources) if sources else None,
            used_context=json.dumps(used_context) if used_context else None,
            llm_model=llm.model  # Use model instead of llm_name
        )
        db.add(assistant_message)
        
        db.commit()
        
        process_time = time.time() - start_time
        logger.info(f"Chat response generated in {process_time:.3f}s - Confidence: {confidence}")
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            used_context=used_context,
            llm=llm.model,  # Use model instead of llm_name
            confidence=confidence,
            session_id=session.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing chat request for user {current_user.email}: {str(e)}", exc_info=True)
        return JSONResponse(content={
            "status": "fallback",
            "message": f"I'm currently unable to answer your question about '{req.question}'. Please try again later."
        }) 