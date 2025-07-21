from fastapi import APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Document, Topic
from app.config import settings
import os
from typing import List
from app.services.cache import cache
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/list-documents")
def list_documents():
    db: Session = SessionLocal()
    try:
        # Try cache first
        cached_docs = cache.get_document_list()
        if cached_docs:
            logger.info("Returning cached document list")
            return cached_docs
        
        docs = db.query(Document).all()
        result = [{
            "id": d.id,
            "file_name": d.file_name,
            "topic": d.topic,
            "page_count": d.page_count,
            "file_size_mb": d.file_size_mb,
            "date_uploaded": d.date_uploaded.isoformat()
        } for d in docs]
        
        # Cache the result
        cache.set_document_list(result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")
    finally:
        db.close()

@router.get("/list-documents/{topic}")
def list_documents_by_topic(topic: str):
    if not topic or len(topic.strip()) == 0:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    db: Session = SessionLocal()
    try:
        # Try cache first
        cached_docs = cache.get_document_list(topic)
        if cached_docs:
            logger.info(f"Returning cached document list for topic: {topic}")
            return cached_docs
        
        docs = db.query(Document).filter(Document.topic == topic).all()
        result = [{
            "id": d.id,
            "file_name": d.file_name,
            "topic": d.topic,
            "page_count": d.page_count,
            "file_size_mb": d.file_size_mb,
            "date_uploaded": d.date_uploaded.isoformat()
        } for d in docs]
        
        # Cache the result
        cache.set_document_list(result, topic)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")
    finally:
        db.close()

@router.get("/list-topics")
def list_topics():
    db: Session = SessionLocal()
    try:
        topics = db.query(Topic).filter(Topic.is_active == True).all()
        topic_list = [{"id": t.id, "name": t.name, "description": t.description} for t in topics]
        return {"topics": topic_list, "count": len(topic_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving topics: {str(e)}")
    finally:
        db.close()

@router.post("/subjects")
def create_subject(
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True)
):
    db: Session = SessionLocal()
    try:
        exists = db.query(Topic).filter(Topic.name == name).first()
        if exists:
            raise HTTPException(status_code=400, detail="Subject already exists")
        topic = Topic(name=name, description=description)
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return {"id": topic.id, "name": topic.name, "description": topic.description}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating subject: {str(e)}")
    finally:
        db.close()

@router.put("/subjects/{topic_id}")
def edit_subject(
    topic_id: int,
    name: str = Body(..., embed=True),
    description: str = Body("", embed=True)
):
    db: Session = SessionLocal()
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Subject not found")
        topic.name = name
        topic.description = description
        db.commit()
        return {"id": topic.id, "name": topic.name, "description": topic.description}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error editing subject: {str(e)}")
    finally:
        db.close()

@router.delete("/subjects/{topic_id}")
def delete_subject(topic_id: int):
    db: Session = SessionLocal()
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Subject not found")
        # Optionally, delete all documents under this topic
        docs = db.query(Document).filter(Document.topic == topic.name).all()
        for doc in docs:
            db.delete(doc)
        db.delete(topic)
        db.commit()
        return {"message": f"Subject '{topic.name}' and all its documents deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting subject: {str(e)}")
    finally:
        db.close()

@router.delete("/delete-document/{id}")
def delete_document(id: int):
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")
        
        # Delete file
        pdf_path = settings.PDF_DIR / doc.topic / doc.file_name
        if pdf_path.exists():
            try:
                pdf_path.unlink()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
        
        # Delete from database
        db.delete(doc)
        db.commit()
        
        return {"status": "deleted", "id": id, "file_name": doc.file_name}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
    finally:
        db.close() 