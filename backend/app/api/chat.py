from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from starlette.concurrency import run_in_threadpool

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    topic: str

@router.post("/chat")
async def chat(req: ChatRequest):
    embedder = EmbeddingService()
    vector_store = VectorStore()
    llm = LLMService()
    q_emb = await run_in_threadpool(embedder.embed_texts, [req.question])
    q_emb = q_emb[0]
    results = await run_in_threadpool(vector_store.similarity_search, req.topic, q_emb, 5)
    docs = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]
    if not docs or not metadatas or not distances or distances[0] < 0.6:
        return {"answer": "I have insufficient knowledge on this topic.", "sources": [], "used_context": [], "llm": llm.llm_name}
    context = "\n".join(docs)
    sources = [f"{m.get('source_file','')}:page {m.get('page','')}" for m in metadatas]
    prompt = f"Context:\n{context}\n\nQuestion: {req.question}\nAnswer:"
    answer = await run_in_threadpool(llm.call_llm, prompt)
    return {
        "answer": answer,
        "sources": sources,
        "used_context": docs,
        "llm": llm.llm_name
    } 