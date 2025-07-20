from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.models.chat import (
    ChatSession, ChatMessage, ChatSessionCreate, ChatSessionResponse,
    ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse
)
from app.utils.logger import logger
from typing import List
import json

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    logger.info(f"User {current_user.email} creating chat session for topic: {session_data.topic}")
    
    try:
        session = ChatSession(
            user_id=current_user.id,
            topic=session_data.topic,
            title=session_data.title
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Chat session {session.id} created for user {current_user.email}")
        
        return ChatSessionResponse(
            id=session.id,
            topic=session.topic,
            title=session.title,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating chat session for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for the current user."""
    try:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).order_by(ChatSession.updated_at.desc()).all()
        
        return [
            ChatSessionResponse(
                id=session.id,
                topic=session.topic,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=len(session.messages)
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error listing chat sessions for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chat sessions"
        )

@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific session."""
    try:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        messages = []
        for msg in session.messages:
            # Parse JSON strings back to lists
            sources = json.loads(msg.sources) if msg.sources else None
            used_context = json.loads(msg.used_context) if msg.used_context else None
            
            messages.append(ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                confidence=msg.confidence,
                sources=sources,
                used_context=used_context,
                llm_model=msg.llm_model,
                created_at=msg.created_at
            ))
        
        return ChatHistoryResponse(
            session=ChatSessionResponse(
                id=session.id,
                topic=session.topic,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=len(session.messages)
            ),
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat history"
        )

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    try:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        session.is_active = False
        db.commit()
        
        logger.info(f"Chat session {session_id} deleted by user {current_user.email}")
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting chat session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def add_message_to_session(
    session_id: int,
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a message to a chat session."""
    try:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        message = ChatMessage(
            session_id=session_id,
            role=message_data.role,
            content=message_data.content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        logger.info(f"Message added to session {session_id} by user {current_user.email}")
        
        return ChatMessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            confidence=message.confidence,
            sources=None,
            used_context=None,
            llm_model=message.llm_model,
            created_at=message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding message to session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message"
        ) 