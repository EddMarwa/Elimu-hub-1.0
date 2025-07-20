import os
import chromadb
from chromadb.config import Settings
from app.config import settings

class VectorStore:
    def __init__(self, persist_directory=None):
        if persist_directory is None:
            persist_directory = str(settings.CHROMA_DIR)
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings(allow_reset=True))

    def get_collection(self, topic):
        return self.client.get_or_create_collection(topic)

    def add_chunks(self, topic, chunks, embeddings, metadatas):
        collection = self.get_collection(topic)
        ids = [f"{topic}_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings.tolist(), ids=ids, metadatas=metadatas)

    def similarity_search(self, topic, query_embedding, top_k=None):
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        collection = self.get_collection(topic)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=['documents', 'metadatas', 'distances'])
        return results 