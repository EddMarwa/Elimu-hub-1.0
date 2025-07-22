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
    
    def search_similar(self, query_embedding: Any, topic_filter: str = None, top_k: int = 5):
        """Search for similar documents across collections or specific topic"""
        try:
            if topic_filter:
                # Search in specific topic collection
                collection = self.get_collection(topic_filter)
                results = collection.query(
                    query_embeddings=[query_embedding], 
                    n_results=top_k, 
                    include=["documents", "metadatas", "distances"]
                )
                
                # Format results
                formatted_results = []
                if results['documents'] and len(results['documents'][0]) > 0:
                    for i, doc in enumerate(results['documents'][0]):
                        formatted_results.append({
                            'content': doc,
                            'source': results['metadatas'][0][i].get('source_file', 'Unknown'),
                            'page': results['metadatas'][0][i].get('page', 0),
                            'score': 1 - results['distances'][0][i]  # Convert distance to similarity score
                        })
                return formatted_results
            else:
                # Search across all collections (topics)
                all_results = []
                collections = self.client.list_collections()
                for collection_info in collections:
                    collection = self.client.get_collection(collection_info.name)
                    results = collection.query(
                        query_embeddings=[query_embedding], 
                        n_results=top_k, 
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    if results['documents'] and len(results['documents'][0]) > 0:
                        for i, doc in enumerate(results['documents'][0]):
                            all_results.append({
                                'content': doc,
                                'source': results['metadatas'][0][i].get('source_file', 'Unknown'),
                                'page': results['metadatas'][0][i].get('page', 0),
                                'score': 1 - results['distances'][0][i],
                                'topic': collection_info.name
                            })
                
                # Sort by score and return top_k
                all_results.sort(key=lambda x: x['score'], reverse=True)
                return all_results[:top_k]
                
        except Exception as e:
            print(f"Error in search_similar: {e}")
            return []

vector_store = VectorStore() 