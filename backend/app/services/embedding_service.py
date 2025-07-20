from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings

class EmbeddingService:
    def __init__(self, model_name=None, chunk_size=None, chunk_overlap=None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.model = SentenceTransformer(self.model_name)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )

    def chunk_text(self, text):
        return self.splitter.split_text(text)

    def embed_texts(self, texts):
        return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True) 