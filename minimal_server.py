#!/usr/bin/env python3
"""
Minimal Elimu Hub Server - Simplified version focused on core PDF knowledge base functionality
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import json
import sqlite3
import requests
from pathlib import Path
import time
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Elimu Hub - Minimal PDF Knowledge Base",
    description="Simple RAG system for PDF documents",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PDF_DIR = DATA_DIR / "pdfs"
PDF_DIR.mkdir(exist_ok=True)

# Simple database setup
DB_PATH = DATA_DIR / "documents.db"

def init_db():
    """Initialize SQLite database with simple schema."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)
    
    # Create topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # Insert default topic
    cursor.execute("""
        INSERT OR IGNORE INTO topics (name, description, created_at)
        VALUES ('General', 'General knowledge base', ?)
    """, (datetime.now().isoformat(),))
    
    conn.commit()
    conn.close()

# Models
class DocumentResponse(BaseModel):
    id: int
    filename: str
    topic: str
    uploaded_at: str

class SearchResponse(BaseModel):
    content: str
    filename: str
    topic: str
    score: float

class ChatRequest(BaseModel):
    question: str
    topic: Optional[str] = None
    max_tokens: Optional[int] = 300

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

# Simple text extraction function
def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from uploaded file."""
    try:
        # For text files
        if filename.endswith('.txt'):
            return file_content.decode('utf-8')
        
        # For PDF files (if PyMuPDF is available)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            # Fallback for PDF without PyMuPDF
            return f"PDF content from {filename} (text extraction not available - install PyMuPDF for full PDF support)"
    
    except Exception as e:
        return f"Error extracting text from {filename}: {str(e)}"

def simple_search(query: str, topic: str = None, limit: int = 5) -> List[dict]:
    """Simple keyword-based search in documents."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    query_words = query.lower().split()
    
    if topic:
        cursor.execute("""
            SELECT filename, topic, content FROM documents 
            WHERE topic = ? AND LOWER(content) LIKE ?
            LIMIT ?
        """, (topic, f"%{' '.join(query_words)}%", limit))
    else:
        cursor.execute("""
            SELECT filename, topic, content FROM documents 
            WHERE LOWER(content) LIKE ?
            LIMIT ?
        """, (f"%{' '.join(query_words)}%", limit))
    
    results = []
    for row in cursor.fetchall():
        filename, topic, content = row
        # Simple scoring based on keyword occurrences
        score = sum(content.lower().count(word) for word in query_words) / len(content)
        
        # Get a snippet around the query
        content_lower = content.lower()
        for word in query_words:
            if word in content_lower:
                start = max(0, content_lower.find(word) - 100)
                end = min(len(content), start + 300)
                snippet = content[start:end]
                break
        else:
            snippet = content[:300]
        
        results.append({
            "content": snippet,
            "filename": filename,
            "topic": topic,
            "score": score
        })
    
    conn.close()
    return sorted(results, key=lambda x: x["score"], reverse=True)

def simple_llm_chat(question: str, context: str = "") -> str:
    """Simple LLM chat using free APIs or fallback responses."""
    
    # Try to use Groq (if API key is available)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": "You are a helpful educational AI assistant. Use the provided context to answer questions accurately."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ]
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json={
                    "model": "llama3-8b-8192",
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Groq API error: {e}")
    
    # Fallback: Simple rule-based responses
    if context:
        return f"Based on the uploaded documents, here's what I found about '{question}':\n\n{context[:500]}...\n\n(Note: Set GROQ_API_KEY in environment for AI-powered responses)"
    else:
        return f"I don't have specific information about '{question}' in the uploaded documents. Please upload relevant PDFs first. (Note: Set GROQ_API_KEY in environment for AI-powered responses)"

# Routes
@app.get("/")
async def root():
    return {"message": "Elimu Hub - Minimal PDF Knowledge Base", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), topic: str = Form("General")):
    """Upload a document to the knowledge base."""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read file content
    content = await file.read()
    
    # Extract text
    text_content = extract_text_from_file(content, file.filename)
    
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")
    
    # Save to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Ensure topic exists
    cursor.execute("""
        INSERT OR IGNORE INTO topics (name, description, created_at)
        VALUES (?, '', ?)
    """, (topic, datetime.now().isoformat()))
    
    # Insert document
    cursor.execute("""
        INSERT INTO documents (filename, topic, content, uploaded_at)
        VALUES (?, ?, ?, ?)
    """, (file.filename, topic, text_content, datetime.now().isoformat()))
    
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Save original file
    file_path = PDF_DIR / f"{doc_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    return DocumentResponse(
        id=doc_id,
        filename=file.filename,
        topic=topic,
        uploaded_at=datetime.now().isoformat()
    )

@app.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, filename, topic, uploaded_at FROM documents
        ORDER BY uploaded_at DESC
    """)
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            "id": row[0],
            "filename": row[1],
            "topic": row[2],
            "uploaded_at": row[3]
        })
    
    conn.close()
    return documents

@app.get("/topics")
async def list_topics():
    """List all topics."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, description FROM topics")
    
    topics = []
    for row in cursor.fetchall():
        topics.append({
            "name": row[0],
            "description": row[1]
        })
    
    conn.close()
    return topics

@app.get("/search")
async def search_documents(query: str, topic: str = None, limit: int = 5):
    """Search documents by keyword."""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = simple_search(query, topic, limit)
    return results

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with the knowledge base using RAG."""
    
    # Search for relevant documents
    search_results = simple_search(request.question, request.topic, 3)
    
    # Combine context from search results
    context = "\n\n".join([f"From {r['filename']}: {r['content']}" for r in search_results])
    
    # Get AI response
    answer = simple_llm_chat(request.question, context)
    
    # Extract source filenames
    sources = [r['filename'] for r in search_results]
    
    return ChatResponse(
        answer=answer,
        sources=sources
    )

@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Count documents
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    # Count topics
    cursor.execute("SELECT COUNT(*) FROM topics")
    topic_count = cursor.fetchone()[0]
    
    # Get recent uploads
    cursor.execute("""
        SELECT filename, topic, uploaded_at FROM documents
        ORDER BY uploaded_at DESC LIMIT 5
    """)
    recent_uploads = [{"filename": row[0], "topic": row[1], "uploaded_at": row[2]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_documents": doc_count,
        "total_topics": topic_count,
        "recent_uploads": recent_uploads,
        "status": "operational"
    }

# API v1 endpoints for frontend compatibility
@app.get("/api/v1/list-topics")
async def api_list_topics():
    """List topics with API v1 prefix for frontend compatibility."""
    return await list_topics()

@app.post("/api/v1/chat")
async def api_chat(request: ChatRequest):
    """Chat endpoint with API v1 prefix for frontend compatibility."""
    return await chat_with_documents(request)

@app.post("/api/v1/llm/chat/completions")
async def api_llm_chat_completions(request: dict):
    """OpenAI-compatible chat completions endpoint."""
    try:
        messages = request.get("messages", [])
        if messages:
            last_message = messages[-1].get("content", "")
            chat_request = ChatRequest(question=last_message, topic="General")
            response = await chat_with_documents(chat_request)
            
            return {
                "id": "chatcmpl-" + str(hash(last_message))[:8],
                "object": "chat.completion",
                "created": int(datetime.utcnow().timestamp()),
                "model": "minimal-rag",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response["answer"]
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(last_message.split()),
                    "completion_tokens": len(response["answer"].split()),
                    "total_tokens": len(last_message.split()) + len(response["answer"].split())
                }
            }
        return {"error": "No messages provided"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/search")
async def api_search_documents(query: str, limit: int = 5):
    """Search documents with API v1 prefix for frontend compatibility."""
    return await search_documents(query, None, limit)

@app.get("/api/v1/documents")
async def api_list_documents():
    """List documents with API v1 prefix for frontend compatibility."""
    return await list_documents()

@app.post("/api/v1/upload")
async def api_upload_document(file: UploadFile = File(...), topic: str = Form("General")):
    """Upload document with API v1 prefix for frontend compatibility."""
    return await upload_document(file, topic)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("📚 Elimu Hub Minimal Server started!")
    print("📊 Database initialized")
    print("🔗 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    print("🚀 Starting Elimu Hub Minimal Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
