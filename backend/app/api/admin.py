from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db, Document, Topic
from app.auth.dependencies import get_current_admin_user
from app.auth.models import User
from app.services.pdf_ingestor import PDFIngestor
from app.services.job_queue import job_queue
from app.config import settings
from app.utils.logger import logger
from typing import List, Optional, Dict, Any
import os
import uuid
import json
from datetime import datetime
import shutil

router = APIRouter()

class AdminStats(BaseModel):
    total_documents: int
    total_topics: int
    total_users: int
    storage_used_mb: float
    recent_uploads: List[Dict]
    system_health: Dict[str, Any]

class TrainingJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    files_processed: int
    total_files: int
    estimated_completion: Optional[str] = None

class KnowledgeBaseStats(BaseModel):
    topic_name: str
    document_count: int
    total_pages: int
    total_size_mb: float
    last_updated: datetime
    embedding_count: int

@router.get("/admin/dashboard/stats")
async def get_admin_dashboard_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive admin dashboard statistics."""
    try:
        from app.auth.models import User as AuthUser
        from app.models.analytics import APIRequest
        
        # Basic counts
        total_documents = db.query(Document).count()
        total_topics = db.query(Topic).filter(Topic.is_active == True).count()
        total_users = db.query(AuthUser).count()
        
        # Storage calculation
        storage_used = 0
        pdf_dir = settings.PDF_DIR
        if pdf_dir.exists():
            for file_path in pdf_dir.rglob("*"):
                if file_path.is_file():
                    storage_used += file_path.stat().st_size
        storage_used_mb = storage_used / (1024 * 1024)
        
        # Recent uploads (last 10)
        recent_docs = db.query(Document).order_by(Document.date_uploaded.desc()).limit(10).all()
        recent_uploads = [
            {
                "id": doc.id,
                "filename": doc.file_name,
                "topic": doc.topic,
                "upload_date": doc.date_uploaded.isoformat(),
                "size_mb": doc.file_size_mb,
                "pages": doc.page_count
            }
            for doc in recent_docs
        ]
        
        # System health check
        system_health = {
            "database": "healthy",
            "vector_store": "healthy",
            "llm": "checking...",
            "storage": "healthy" if storage_used_mb < 10000 else "warning"  # 10GB limit
        }
        
        # Check LLM health
        try:
            from app.services.llm_service import LLMService
            llm = LLMService()
            test_response = llm.call_llm("Test", max_tokens=5, temp=0.1)
            system_health["llm"] = "healthy" if not test_response.startswith("[LLM ERROR]") else "error"
        except Exception:
            system_health["llm"] = "error"
        
        return AdminStats(
            total_documents=total_documents,
            total_topics=total_topics,
            total_users=total_users,
            storage_used_mb=round(storage_used_mb, 2),
            recent_uploads=recent_uploads,
            system_health=system_health
        )
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard statistics")

@router.post("/admin/upload/training-files", response_model=TrainingJobResponse)
async def upload_training_files(
    background_tasks: BackgroundTasks,
    topic: str = Form(...),
    description: str = Form(""),
    files: List[UploadFile] = File(...),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Upload multiple PDF files for training the knowledge base."""
    try:
        # Validate files
        valid_files = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            if file.size > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds size limit")
            valid_files.append(file)
        
        # Create or get topic
        db_topic = db.query(Topic).filter(Topic.name == topic).first()
        if not db_topic:
            db_topic = Topic(name=topic, description=description, is_active=True)
            db.add(db_topic)
            db.commit()
            db.refresh(db_topic)
        
        # Create job ID
        job_id = str(uuid.uuid4())
        
        # Save files temporarily
        temp_files = []
        topic_dir = settings.PDF_DIR / topic
        topic_dir.mkdir(exist_ok=True)
        
        for file in valid_files:
            temp_filename = f"{uuid.uuid4()}_{file.filename}"
            temp_path = topic_dir / temp_filename
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            temp_files.append({
                "path": str(temp_path),
                "original_name": file.filename,
                "size": file.size
            })
        
        # Submit background job for processing
        def process_training_files():
            try:
                ingestor = PDFIngestor()
                total_files = len(temp_files)
                
                for i, file_info in enumerate(temp_files):
                    logger.info(f"Processing file {i+1}/{total_files}: {file_info['original_name']}")
                    
                    # Process the PDF
                    result = ingestor.ingest_pdf(file_info["path"], topic)
                    
                    # Create document record
                    doc = Document(
                        file_name=file_info["original_name"],
                        topic=topic,
                        page_count=result.get("pages", 0),
                        file_size_mb=file_info["size"] / (1024 * 1024),
                        date_uploaded=datetime.utcnow()
                    )
                    db.add(doc)
                
                db.commit()
                logger.info(f"Training job {job_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Training job {job_id} failed: {e}")
                raise
        
        # Submit the job
        background_tasks.add_task(process_training_files)
        
        logger.info(f"Admin {current_admin.email} started training job {job_id} with {len(valid_files)} files")
        
        return TrainingJobResponse(
            job_id=job_id,
            status="processing",
            message=f"Processing {len(valid_files)} files for topic '{topic}'",
            files_processed=0,
            total_files=len(valid_files),
            estimated_completion="5-10 minutes"
        )
        
    except Exception as e:
        logger.error(f"Error uploading training files: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")

@router.get("/admin/knowledge-base/overview")
async def get_knowledge_base_overview(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get overview of the knowledge base by topic."""
    try:
        from app.services.vector_store import VectorStore
        
        topics = db.query(Topic).filter(Topic.is_active == True).all()
        knowledge_base_stats = []
        
        vector_store = VectorStore()
        
        for topic in topics:
            # Get document stats for this topic
            topic_docs = db.query(Document).filter(Document.topic == topic.name).all()
            
            total_pages = sum(doc.page_count for doc in topic_docs)
            total_size_mb = sum(doc.file_size_mb for doc in topic_docs)
            last_updated = max([doc.date_uploaded for doc in topic_docs]) if topic_docs else None
            
            # Get embedding count from vector store
            try:
                embedding_count = vector_store.get_collection_size(topic.name)
            except:
                embedding_count = 0
            
            knowledge_base_stats.append(KnowledgeBaseStats(
                topic_name=topic.name,
                document_count=len(topic_docs),
                total_pages=total_pages,
                total_size_mb=round(total_size_mb, 2),
                last_updated=last_updated or datetime.utcnow(),
                embedding_count=embedding_count
            ))
        
        return {
            "total_topics": len(topics),
            "total_documents": sum(stat.document_count for stat in knowledge_base_stats),
            "total_embeddings": sum(stat.embedding_count for stat in knowledge_base_stats),
            "topics": knowledge_base_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge base overview: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving knowledge base overview")

@router.delete("/admin/knowledge-base/{topic_name}")
async def delete_knowledge_base_topic(
    topic_name: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete an entire topic from the knowledge base."""
    try:
        # Get topic
        topic = db.query(Topic).filter(Topic.name == topic_name).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Delete documents from database
        documents = db.query(Document).filter(Document.topic == topic_name).all()
        for doc in documents:
            db.delete(doc)
        
        # Delete topic
        db.delete(topic)
        db.commit()
        
        # Delete vector embeddings
        try:
            from app.services.vector_store import VectorStore
            vector_store = VectorStore()
            vector_store.delete_collection(topic_name)
        except Exception as e:
            logger.warning(f"Error deleting vector collection for {topic_name}: {e}")
        
        # Delete PDF files
        topic_dir = settings.PDF_DIR / topic_name
        if topic_dir.exists():
            shutil.rmtree(topic_dir)
        
        logger.info(f"Admin {current_admin.email} deleted topic: {topic_name}")
        
        return {"message": f"Topic '{topic_name}' deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting topic {topic_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting topic: {str(e)}")

@router.post("/admin/knowledge-base/retrain/{topic_name}")
async def retrain_topic(
    topic_name: str,
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Retrain embeddings for a specific topic."""
    try:
        # Check if topic exists
        topic = db.query(Topic).filter(Topic.name == topic_name).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Get all PDFs for this topic
        topic_dir = settings.PDF_DIR / topic_name
        if not topic_dir.exists():
            raise HTTPException(status_code=404, detail="No files found for this topic")
        
        pdf_files = list(topic_dir.glob("*.pdf"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="No PDF files found for this topic")
        
        job_id = str(uuid.uuid4())
        
        def retrain_embeddings():
            try:
                from app.services.vector_store import VectorStore
                from app.services.pdf_ingestor import PDFIngestor
                
                # Delete existing embeddings
                vector_store = VectorStore()
                vector_store.delete_collection(topic_name)
                
                # Re-ingest all files
                ingestor = PDFIngestor()
                for pdf_file in pdf_files:
                    logger.info(f"Retraining: {pdf_file.name}")
                    ingestor.ingest_pdf(str(pdf_file), topic_name)
                
                logger.info(f"Retrain job {job_id} completed for topic {topic_name}")
                
            except Exception as e:
                logger.error(f"Retrain job {job_id} failed: {e}")
                raise
        
        background_tasks.add_task(retrain_embeddings)
        
        logger.info(f"Admin {current_admin.email} started retrain job for topic: {topic_name}")
        
        return {
            "job_id": job_id,
            "message": f"Retraining started for topic '{topic_name}'",
            "files_count": len(pdf_files),
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error retraining topic {topic_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retraining topic: {str(e)}")

@router.get("/admin/system/logs")
async def get_system_logs(
    lines: int = 100,
    current_admin: User = Depends(get_current_admin_user)
):
    """Get recent system logs."""
    try:
        log_file = settings.BASE_DIR / "logs" / "app.log"
        
        if not log_file.exists():
            return {"logs": [], "message": "No log file found"}
        
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(all_lines),
            "showing_lines": len(recent_lines)
        }
        
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        raise HTTPException(status_code=500, detail="Error reading system logs")
