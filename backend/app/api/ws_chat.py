from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.models.chat import ChatSession, ChatMessage
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.config import settings
from app.utils.logger import logger
from typing import Optional
import json

router = APIRouter()

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: int,
    db: Session = Depends(get_db)
):
    await websocket.accept()
    user: Optional[User] = None
    try:
        # Expect the first message to be the JWT token
        token_data = await websocket.receive_text()
        from app.auth.utils import verify_token
        payload = verify_token(token_data)
        if not payload:
            await websocket.send_text(json.dumps({"error": "Invalid token"}))
            await websocket.close()
            return
        user_id = payload["user_id"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            await websocket.send_text(json.dumps({"error": "Invalid user"}))
            await websocket.close()
            return
        logger.info(f"WebSocket connection established for user {user.email} on session {session_id}")
        
        # Main loop: receive user messages and stream assistant responses
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            question = data_json.get("question")
            topic = data_json.get("topic")
            if not question or not topic:
                await websocket.send_text(json.dumps({"error": "Missing question or topic"}))
                continue
            
            # Save user message
            user_message = ChatMessage(
                session_id=session_id,
                role="user",
                content=question
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)
            
            # RAG pipeline (streaming simulation)
            embedder = EmbeddingService()
            vector_store = VectorStore()
            llm = LLMService()
            q_emb = embedder.embed_texts([question])[0]
            results = vector_store.similarity_search(topic, q_emb, settings.TOP_K_RESULTS)
            docs = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            if not docs or not metadatas or not distances or distances[0] > settings.SIMILARITY_THRESHOLD:
                answer = "I don't have sufficient information to answer your question."
                sources = []
                used_context = []
                confidence = None
            else:
                context = "\n".join(docs)
                sources = [f"{m.get('source_file','')}:page {m.get('page','')}" for m in metadatas]
                prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
                # Simulate streaming by sending partial responses
                answer = ""
                for chunk in llm.call_llm(prompt).split():
                    answer += chunk + " "
                    await websocket.send_text(json.dumps({"partial": answer.strip()}))
                confidence = 1.0 - distances[0] if distances else None
                used_context = docs
            # Save assistant message
            assistant_message = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=answer.strip(),
                confidence=confidence,
                sources=json.dumps(sources) if sources else None,
                used_context=json.dumps(used_context) if used_context else None,
                llm_model=llm.llm_name
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            # Send final response
            await websocket.send_text(json.dumps({
                "answer": answer.strip(),
                "sources": sources,
                "used_context": used_context,
                "llm": llm.llm_name,
                "confidence": confidence
            }))
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user.email if user else 'unknown'} on session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"error": str(e)}))
        await websocket.close() 