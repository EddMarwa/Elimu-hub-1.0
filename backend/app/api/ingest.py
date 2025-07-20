from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Document
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
import os
try:
    import fitz  # PyMuPDF
except ImportError:
    from PyMuPDF import fitz
from datetime import datetime

router = APIRouter()

PDF_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/pdfs'))
CHROMA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/chroma'))

@router.post("/ingest/{topic}")
async def ingest_topic(topic: str, files: list[UploadFile] = File(...)):
    os.makedirs(os.path.join(PDF_ROOT, topic), exist_ok=True)
    db: Session = SessionLocal()
    embedder = EmbeddingService()
    vector_store = VectorStore(persist_directory=CHROMA_ROOT)
    results = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF.")
        file_path = os.path.join(PDF_ROOT, topic, file.filename)
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        # Extract PDF metadata
        pdf = fitz.open(file_path)
        page_count = pdf.page_count
        all_chunks = []
        all_metadatas = []
        for page_num in range(page_count):
            page = pdf.load_page(page_num)
            text = page.get_text()
            if not text.strip():
                continue
            chunks = embedder.chunk_text(text)
            all_chunks.extend(chunks)
            all_metadatas.extend([
                {"source_file": file.filename, "page": page_num + 1} for _ in chunks
            ])
        pdf.close()
        file_size_mb = round(os.path.getsize(file_path) / 1024 / 1024, 2)
        doc = Document(
            file_name=file.filename,
            topic=topic,
            page_count=page_count,
            file_size_mb=file_size_mb,
            date_uploaded=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        # Embed and store in Chroma
        if all_chunks:
            embeddings = embedder.embed_texts(all_chunks)
            vector_store.add_chunks(topic, all_chunks, embeddings, all_metadatas)
        results.append({
            "id": doc.id,
            "file_name": doc.file_name,
            "topic": doc.topic,
            "page_count": doc.page_count,
            "file_size_mb": doc.file_size_mb,
            "date_uploaded": doc.date_uploaded.isoformat()
        })
    db.close()
    return {"uploaded": results} 