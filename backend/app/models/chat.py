from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    title = Column(String, nullable=True)  # Auto-generated from first message
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    sources = Column(Text, nullable=True)  # JSON string of sources
    used_context = Column(Text, nullable=True)  # JSON string of context
    llm_model = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

# Pydantic models for API
class ChatSessionCreate(BaseModel):
    topic: str
    title: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: int
    topic: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int

class ChatMessageCreate(BaseModel):
    content: str
    role: str = "user"

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    confidence: Optional[float]
    sources: Optional[List[str]]
    used_context: Optional[List[str]]
    llm_model: Optional[str]
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse] 