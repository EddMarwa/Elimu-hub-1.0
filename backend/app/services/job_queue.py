import asyncio
import threading
import queue
import time
from typing import Callable, Any, Dict, Optional, List
from datetime import datetime
from enum import Enum
from app.utils.logger import logger
import json
from app.services.cache import cache
from app.api.upload_progress import send_upload_progress

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Job:
    def __init__(self, job_id: str, func: Callable, args: tuple = (), kwargs: dict = None):
        self.job_id = job_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.status = JobStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.progress = 0.0
        self.metadata = {}

class JobQueue:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.jobs: Dict[str, Job] = {}
        self.job_queue = queue.Queue()
        self.workers = []
        self.running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start the job queue workers."""
        if self.running:
            return
        
        self.running = True
        logger.info(f"Starting job queue with {self.max_workers} workers")
        
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop the job queue workers."""
        self.running = False
        logger.info("Stopping job queue workers")
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
    
    def _worker(self, worker_id: int):
        """Worker thread function."""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get job from queue with timeout
                job = self.job_queue.get(timeout=1)
                self._process_job(job, worker_id)
                self.job_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Worker {worker_id} stopped")
    
    def _process_job(self, job: Job, worker_id: int):
        """Process a single job."""
        try:
            with self._lock:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.utcnow()
            
            logger.info(f"Worker {worker_id} processing job {job.job_id}")
            
            # Execute the job function
            if asyncio.iscoroutinefunction(job.func):
                # Handle async functions
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    job.result = loop.run_until_complete(job.func(*job.args, **job.kwargs))
                finally:
                    loop.close()
            else:
                # Handle sync functions
                job.result = job.func(*job.args, **job.kwargs)
            
            with self._lock:
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.progress = 100.0
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.utcnow()
            
            logger.error(f"Job {job.job_id} failed: {e}")
    
    def submit_job(self, job_id: str, func: Callable, args: tuple = (), kwargs: dict = None) -> str:
        """Submit a new job to the queue."""
        job = Job(job_id, func, args, kwargs)
        
        with self._lock:
            self.jobs[job_id] = job
        
        self.job_queue.put(job)
        logger.info(f"Job {job_id} submitted to queue")
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a job."""
        # Try cache first
        cached_status = cache.get_job_status(job_id)
        if cached_status:
            return cached_status
        
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        status = {
            "job_id": job.job_id,
            "status": job.status.value,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error": job.error,
            "metadata": job.metadata
        }
        
        # Cache the status
        cache.set_job_status(job_id, status)
        return status
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = self.jobs.get(job_id)
        if not job or job.status != JobStatus.PENDING:
            return False
        
        with self._lock:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
        
        logger.info(f"Job {job_id} cancelled")
        return True
    
    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Dict[str, Any]]:
        """List all jobs, optionally filtered by status."""
        jobs = []
        
        with self._lock:
            for job in self.jobs.values():
                if status is None or job.status == status:
                    jobs.append(self.get_job_status(job.job_id))
        
        return jobs

# Global job queue instance
job_queue = JobQueue() 