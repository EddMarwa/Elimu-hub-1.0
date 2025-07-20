from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.auth.dependencies import get_current_admin_user
from app.auth.models import User
from app.services.analytics import analytics
from app.models.analytics import AnalyticsSummary
from app.utils.logger import logger
from typing import Dict, Any

router = APIRouter()

@router.get("/analytics/summary", response_model=Dict[str, Any])
async def get_analytics_summary(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get analytics summary for the last N hours (admin only)."""
    try:
        summary = analytics.get_analytics_summary(hours)
        logger.info(f"Admin user {current_user.email} accessed analytics summary")
        return summary
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics summary"
        )

@router.get("/analytics/system-metrics", response_model=Dict[str, float])
async def get_system_metrics(
    current_user: User = Depends(get_current_admin_user)
):
    """Get current system metrics (admin only)."""
    try:
        metrics = analytics.get_system_metrics()
        logger.info(f"Admin user {current_user.email} accessed system metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system metrics"
        )

@router.get("/analytics/health")
async def analytics_health():
    """Health check for analytics service."""
    try:
        # Quick test of analytics service
        summary = analytics.get_analytics_summary(1)
        return {"status": "healthy", "analytics_enabled": analytics.enabled}
    except Exception as e:
        logger.error(f"Analytics health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)} 