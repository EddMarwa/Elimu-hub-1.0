import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME

class PDFIngestor:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text

    def chunk_text(self, text):
        return self.splitter.split_text(text)

    def embed_chunks(self, chunks):
        return self.model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)

    def process_pdf(self, pdf_path):
        text = self.extract_text(pdf_path)
        chunks = self.chunk_text(text)
        embeddings = self.embed_chunks(chunks)
        return chunks, embeddings 