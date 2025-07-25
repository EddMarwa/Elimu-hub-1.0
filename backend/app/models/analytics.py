from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.db.database import Base

class APIRequest(Base):
    __tablename__ = "api_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for unauthenticated
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)  # in seconds
    request_size = Column(Integer, nullable=True)  # in bytes
    response_size = Column(Integer, nullable=True)  # in bytes
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # login, logout, upload, chat, search
    details = Column(Text, nullable=True)  # JSON string with additional details
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False)  # cpu_usage, memory_usage, active_users
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)  # percentage, bytes, count
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models for API
class APIRequestResponse(BaseModel):
    id: int
    user_id: Optional[int]
    endpoint: str
    method: str
    status_code: int
    response_time: float
    request_size: Optional[int]
    response_size: Optional[int]
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    activity_type: str
    details: Optional[str]
    created_at: datetime

class SystemMetricsResponse(BaseModel):
    id: int
    metric_name: str
    metric_value: float
    metric_unit: Optional[str]
    created_at: datetime

class AnalyticsSummary(BaseModel):
    total_requests: int
    unique_users: int
    avg_response_time: float
    error_rate: float
    top_endpoints: list
    recent_activities: list 