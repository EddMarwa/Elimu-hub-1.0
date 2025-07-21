# backend/app/models/document.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    file_type = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=func.now())