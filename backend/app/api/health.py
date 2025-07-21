from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import psutil
import os
from pathlib import Path
from app.config import settings

router = APIRouter(tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    system: Dict[str, Any]
    database: str
    storage: Dict[str, Any]

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    """
    import datetime
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Database check
    db_status = "healthy"
    try:
        # Check if database file exists
        if settings.DATABASE_URL.startswith("sqlite"):
            db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")
            if not Path(db_path).parent.exists():
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            db_status = "healthy" if Path(db_path).exists() else "initializing"
    except Exception:
        db_status = "error"
    
    # Storage check
    data_dir = Path(settings.DATA_DIR)
    pdf_dir = Path(settings.PDF_DIR)
    chroma_dir = Path(settings.CHROMA_DIR)
    
    storage_info = {
        "data_directory": str(data_dir),
        "pdf_directory": str(pdf_dir),
        "vector_directory": str(chroma_dir),
        "data_dir_exists": data_dir.exists(),
        "pdf_dir_exists": pdf_dir.exists(),
        "chroma_dir_exists": chroma_dir.exists(),
        "disk_usage_percent": disk.percent,
        "free_space_gb": round(disk.free / (1024**3), 2)
    }
    
    # Overall status
    overall_status = "healthy"
    if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
        overall_status = "warning"
    if db_status == "error":
        overall_status = "error"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.datetime.utcnow().isoformat(),
        version="1.0.0",
        system={
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "processes": len(psutil.pids())
        },
        database=db_status,
        storage=storage_info
    )
