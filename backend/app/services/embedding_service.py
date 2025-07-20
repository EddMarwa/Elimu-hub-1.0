from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

class EmbeddingService:
    def __init__(self, model_name='BAAI/bge-m3', chunk_size=250, chunk_overlap=40):
        self.model = SentenceTransformer(model_name)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def chunk_text(self, text):
        return self.splitter.split_text(text)

    def embed_texts(self, texts):
        return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True) 