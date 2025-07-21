from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Document, Topic
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.config import settings
from app.utils.logger import logger
import os
try:
    import fitz  # PyMuPDF
except ImportError:
    from PyMuPDF import fitz
from datetime import datetime
from app.db.fts import insert_document_content
from app.services.cache import cache
from app.api.upload_progress import send_upload_progress
from app.services.job_queue import job_queue
from app.services.analytics import analytics
from app.services.pdf_ingestor import pdf_ingestor
from app.services.cache_service import cache_service
import uuid

router = APIRouter()

@router.post("/ingest")
async def ingest_document(
    topic_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Ingest a PDF document."""
    db: Session = SessionLocal()
    try:
        # Validate topic
        topic = db.query(Topic).filter(Topic.id == topic_id, Topic.is_active == True).first()
        if not topic:
            raise HTTPException(status_code=400, detail="Invalid topic ID")
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create job for processing
        job_id = str(uuid.uuid4())
        
        # Save file temporarily
        temp_path = f"temp_{job_id}.pdf"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Submit job to queue
        job_queue.submit_job(
            job_id=job_id,
            func=process_ingest_job,
            args=(temp_path, current_user.id, job_id, topic.name)
        )
        
        # Log user activity
        analytics.log_user_activity(
            user_id=current_user.id,
            activity_type="upload",
            details={"filename": file.filename, "job_id": job_id}
        )
        
        return {
            "message": "Document uploaded successfully",
            "job_id": job_id,
            "status": "pending",
            "topic": topic.name
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {str(e)}"
        )
    finally:
        db.close()

async def process_ingest_job(file_path: str, user_id: int, job_id: str, topic_name: str):
    """Process document ingestion with progress tracking."""
    try:
        # Send initial progress
        await send_upload_progress(user_id, job_id, {
            "status": "processing", 
            "progress": 10, 
            "message": "Starting document processing..."
        })
        
        # Extract text from PDF
        await send_upload_progress(user_id, job_id, {
            "status": "processing", 
            "progress": 30, 
            "message": "Extracting text from PDF..."
        })
        
        text = pdf_ingestor.extract_text(file_path)
        if not text:
            raise Exception("Failed to extract text from PDF")
        
        # Generate embeddings
        await send_upload_progress(user_id, job_id, {
            "status": "processing", 
            "progress": 60, 
            "message": "Generating embeddings..."
        })
        
        embeddings = EmbeddingService().generate_embeddings(text)
        
        # Store in vector database
        await send_upload_progress(user_id, job_id, {
            "status": "processing", 
            "progress": 80, 
            "message": "Storing in vector database..."
        })
        
        VectorStore(persist_directory=str(settings.CHROMA_DIR)).add_documents([text], embeddings)
        
        # Update cache
        await send_upload_progress(user_id, job_id, {
            "status": "processing", 
            "progress": 90, 
            "message": "Updating cache..."
        })
        
        cache_service.invalidate_documents_cache()
        
        # Complete
        await send_upload_progress(user_id, job_id, {
            "status": "completed", 
            "progress": 100, 
            "message": "Document processed successfully"
        })
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        error_msg = f"Job failed: {str(e)}"
        await send_upload_progress(user_id, job_id, {
            "status": "failed", 
            "progress": 0, 
            "message": error_msg
        })
        logger.error(f"Job {job_id} failed: {e}")
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path) 