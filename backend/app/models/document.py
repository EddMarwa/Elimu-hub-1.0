# backend/app/models/document.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import Base

# Removed duplicate Document model. Use Document from app.db.database instead.
# from app.db.database import Document