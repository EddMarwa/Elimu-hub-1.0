from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Document
import os

router = APIRouter()

@router.get("/list-documents")
def list_documents():
    db: Session = SessionLocal()
    docs = db.query(Document).all()
    db.close()
    return [{
        "id": d.id,
        "file_name": d.file_name,
        "topic": d.topic,
        "page_count": d.page_count,
        "file_size_mb": d.file_size_mb,
        "date_uploaded": d.date_uploaded.isoformat()
    } for d in docs]

@router.get("/list-documents/{topic}")
def list_documents_by_topic(topic: str):
    db: Session = SessionLocal()
    docs = db.query(Document).filter(Document.topic == topic).all()
    db.close()
    return [{
        "id": d.id,
        "file_name": d.file_name,
        "topic": d.topic,
        "page_count": d.page_count,
        "file_size_mb": d.file_size_mb,
        "date_uploaded": d.date_uploaded.isoformat()
    } for d in docs]

@router.delete("/delete-document/{id}")
def delete_document(id: int):
    db: Session = SessionLocal()
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found.")
    # Delete file
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f'../../data/pdfs/{doc.topic}/{doc.file_name}'))
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    db.delete(doc)
    db.commit()
    db.close()
    return {"status": "deleted", "id": id} 