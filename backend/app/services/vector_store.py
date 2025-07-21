import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os

class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma/"):
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.Client(Settings(persist_directory=persist_directory))
        self.persist_directory = persist_directory

    def get_collection(self, topic: str):
        return self.client.get_or_create_collection(topic)

    def add_documents(self, topic: str, chunks: List[Dict], embeddings: List[Any]):
        collection = self.get_collection(topic)
        ids = [f"{chunk['source_file']}_{chunk['page']}_{i}" for i, chunk in enumerate(chunks)]
        metadatas = [{"source_file": chunk["source_file"], "page": chunk["page"]} for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        collection.add(documents=documents, embeddings=embeddings, ids=ids, metadatas=metadatas)

    def query(self, topic: str, query_embedding: Any, top_k: int = 5):
        collection = self.get_collection(topic)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["documents", "metadatas", "distances"])
        return results

vector_store = VectorStore() 