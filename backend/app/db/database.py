import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime
from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(Text, nullable=False)
    topic = Column(Text, nullable=False)
    page_count = Column(Integer, nullable=False)
    file_size_mb = Column(Float, nullable=False)
    date_uploaded = Column(DateTime, default=datetime.utcnow)

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

# Import all models to ensure they're included in table creation
from app.auth.models import User
from app.models.chat import ChatSession, ChatMessage
from app.models.analytics import APIRequest, UserActivity, SystemMetrics

# Create all tables
Base.metadata.create_all(bind=engine) 