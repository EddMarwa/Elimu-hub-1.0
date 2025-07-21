import fitz  # PyMuPDF
from typing import List, Dict
import os

class PDFIngestor:
    def __init__(self, chunk_size: int = 300):
        self.chunk_size = chunk_size

    def extract_text_chunks(self, pdf_path: str) -> List[Dict]:
        """
        Extracts text from a PDF and splits it into chunks with metadata.
        Returns a list of dicts: { 'text': ..., 'page': ..., 'source_file': ... }
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        doc = fitz.open(pdf_path)
        chunks = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            # Split text into chunks of roughly self.chunk_size words
            words = text.split()
            for i in range(0, len(words), self.chunk_size):
                chunk_text = ' '.join(words[i:i+self.chunk_size])
                if chunk_text.strip():
                    chunks.append({
                        'text': chunk_text,
                        'page': page_num + 1,
                        'source_file': os.path.basename(pdf_path)
                    })
        return chunks

pdf_ingestor = PDFIngestor() 