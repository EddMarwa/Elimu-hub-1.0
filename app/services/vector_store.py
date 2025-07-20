import os
import chromadb
from chromadb.config import Settings
from app.config import CHROMA_DB_DIR, CHROMA_COLLECTION_PREFIX

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR, settings=Settings(allow_reset=True))

    def get_collection(self, topic):
        name = CHROMA_COLLECTION_PREFIX + topic.lower().replace(' ', '_')
        return self.client.get_or_create_collection(name)

    def add_documents(self, topic, chunks, embeddings):
        collection = self.get_collection(topic)
        ids = [f"{topic}_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings.tolist(), ids=ids)

    def similarity_search(self, topic, query_embedding, top_k=5):
        collection = self.get_collection(topic)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results

    def delete_topic(self, topic):
        name = CHROMA_COLLECTION_PREFIX + topic.lower().replace(' ', '_')
        self.client.delete_collection(name) 