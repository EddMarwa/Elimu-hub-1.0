import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.analytics import APIRequest, UserActivity, SystemMetrics
from app.utils.logger import logger
import psutil

class AnalyticsService:
    def __init__(self):
        self.enabled = True  # Can be controlled via config
    
    def log_api_request(
        self,
        user_id: Optional[int],
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log an API request to the database."""
        if not self.enabled:
            return
        
        try:
            db = SessionLocal()
            request = APIRequest(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address
            )
            db.add(request)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging API request: {e}")
        finally:
            db.close()
    
    def log_user_activity(
        self,
        user_id: int,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log user activity to the database."""
        if not self.enabled:
            return
        
        try:
            db = SessionLocal()
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                details=json.dumps(details) if details else None
            )
            db.add(activity)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging user activity: {e}")
        finally:
            db.close()
    
    def log_system_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None
    ):
        """Log system metric to the database."""
        if not self.enabled:
            return
        
        try:
            db = SessionLocal()
            metric = SystemMetrics(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit
            )
            db.add(metric)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging system metric: {e}")
        finally:
            db.close()
    
    def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for the last N hours."""
        try:
            db = SessionLocal()
            since = datetime.utcnow() - timedelta(hours=hours)
            
            # Total requests
            total_requests = db.query(APIRequest).filter(
                APIRequest.created_at >= since
            ).count()
            
            # Unique users
            unique_users = db.query(APIRequest.user_id).filter(
                APIRequest.created_at >= since,
                APIRequest.user_id.isnot(None)
            ).distinct().count()
            
            # Average response time
            avg_response_time = db.query(APIRequest.response_time).filter(
                APIRequest.created_at >= since
            ).scalar()
            avg_response_time = avg_response_time or 0.0
            
            # Error rate
            total_requests_for_error = db.query(APIRequest).filter(
                APIRequest.created_at >= since
            ).count()
            error_requests = db.query(APIRequest).filter(
                APIRequest.created_at >= since,
                APIRequest.status_code >= 400
            ).count()
            error_rate = (error_requests / total_requests_for_error * 100) if total_requests_for_error > 0 else 0
            
            # Top endpoints
            top_endpoints = db.query(
                APIRequest.endpoint,
                db.func.count(APIRequest.id).label('count')
            ).filter(
                APIRequest.created_at >= since
            ).group_by(APIRequest.endpoint).order_by(
                db.func.count(APIRequest.id).desc()
            ).limit(10).all()
            
            # Recent activities
            recent_activities = db.query(UserActivity).filter(
                UserActivity.created_at >= since
            ).order_by(UserActivity.created_at.desc()).limit(20).all()
            
            return {
                "total_requests": total_requests,
                "unique_users": unique_users,
                "avg_response_time": round(avg_response_time, 3),
                "error_rate": round(error_rate, 2),
                "top_endpoints": [{"endpoint": ep.endpoint, "count": ep.count} for ep in top_endpoints],
                "recent_activities": [
                    {
                        "id": act.id,
                        "user_id": act.user_id,
                        "activity_type": act.activity_type,
                        "details": act.details,
                        "created_at": act.created_at.isoformat()
                    }
                    for act in recent_activities
                ]
            }
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
        finally:
            db.close()
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Log metrics
            self.log_system_metric("cpu_usage", cpu_percent, "percentage")
            self.log_system_metric("memory_usage", memory_percent, "percentage")
            self.log_system_metric("disk_usage", disk_percent, "percentage")
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "disk_usage": disk_percent,
                "memory_available_gb": round(memory.available / (1024**3), 2)
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}

# Global analytics service instance
analytics = AnalyticsService() 