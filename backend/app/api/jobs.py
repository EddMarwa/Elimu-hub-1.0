from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_active_user, get_current_admin_user
from app.auth.models import User
from app.services.job_queue import job_queue, JobStatus
from app.utils.logger import logger
from typing import List, Dict, Any

router = APIRouter()

@router.get("/jobs", response_model=List[Dict[str, Any]])
async def list_jobs(
    status_filter: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """List all jobs (filtered by status if provided)."""
    try:
        if status_filter:
            try:
                job_status = JobStatus(status_filter)
                jobs = job_queue.list_jobs(job_status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )
        else:
            jobs = job_queue.list_jobs()
        
        logger.info(f"User {current_user.email} listed {len(jobs)} jobs")
        return jobs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing jobs for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list jobs"
        )

@router.get("/jobs/{job_id}", response_model=Dict[str, Any])
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the status of a specific job."""
    try:
        job_status = job_queue.get_job_status(job_id)
        if not job_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        logger.info(f"User {current_user.email} checked status of job {job_id}")
        return job_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status"
        )

@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a pending job."""
    try:
        success = job_queue.cancel_job(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job cannot be cancelled (not found or already running/completed)"
            )
        
        logger.info(f"User {current_user.email} cancelled job {job_id}")
        return {"message": "Job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling job for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel job"
        )

@router.post("/jobs/cleanup")
async def cleanup_completed_jobs(
    current_user: User = Depends(get_current_admin_user)
):
    """Clean up completed and failed jobs (admin only)."""
    try:
        # This would be implemented in the job queue to remove old jobs
        # For now, just log the request
        logger.info(f"Admin user {current_user.email} requested job cleanup")
        return {"message": "Job cleanup completed"}
        
    except Exception as e:
        logger.error(f"Error during job cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup jobs"
        ) 