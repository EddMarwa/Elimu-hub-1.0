import subprocess
import numpy as np
from app.config import LLM_MODEL_PATH, LLAMA_CPP_PATH, SIMILARITY_THRESHOLD
from app.services.vector_store import VectorStore
from sentence_transformers import SentenceTransformer

class ChatService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedder = SentenceTransformer('BAAI/bge-m3')

    def retrieve_context(self, topic, question, top_k=5):
        q_emb = self.embedder.encode([question])[0]
        results = self.vector_store.similarity_search(topic, q_emb, top_k=top_k)
        if not results['documents'] or not results['embeddings']:
            return [], 0.0
        # Compute max similarity
        max_sim = max(np.dot(q_emb, np.array(results['embeddings'][0]).T) / (np.linalg.norm(q_emb) * np.linalg.norm(results['embeddings'][0])), default=0.0)
        return results['documents'][0], max_sim

    def call_llm(self, prompt):
        # Call llama.cpp via subprocess
        cmd = [LLAMA_CPP_PATH, "-m", LLM_MODEL_PATH, "-p", prompt, "--temp", "0.2", "-n", "512"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout.strip()

    def answer(self, topic, question):
        context, max_sim = self.retrieve_context(topic, question)
        if max_sim < SIMILARITY_THRESHOLD:
            return "I have insufficient knowledge on this topic."
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        return self.call_llm(prompt) 