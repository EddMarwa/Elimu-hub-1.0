from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_ingestor import PDFIngestor
from app.services.vector_store import VectorStore
from app.config import PDF_DIR
import os

router = APIRouter()

@router.post("/ingest/{topic}")
def ingest_topic(topic: str, files: list[UploadFile] = File(...)):
    os.makedirs(PDF_DIR, exist_ok=True)
    ingestor = PDFIngestor()
    vector_store = VectorStore()
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        pdf_path = os.path.join(PDF_DIR, f"{topic}_{file.filename}")
        with open(pdf_path, "wb") as f:
            f.write(file.file.read())
        chunks, embeddings = ingestor.process_pdf(pdf_path)
        vector_store.add_documents(topic, chunks, embeddings)
    return {"status": "success", "message": f"Ingested {len(files)} PDFs for topic '{topic}'"} 