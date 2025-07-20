# Elimu Hub Document Management Backend

A FastAPI backend for uploading, tracking, and managing topic-specific PDF documents for Elimu Hub, with vector search and local LLM chat.

## Features
- Upload PDFs by topic, auto-organized in backend/data/pdfs/{topic}
- Extract and store PDF metadata in SQLite (backend/data/documents.db)
- List all documents or by topic
- Delete PDFs and their records
- **Vector search**: ChromaDB stores embeddings per topic
- **Chat endpoint**: Retrieve context and call local LLM (Llama/Mistral)

## Setup
1. Install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints
### Upload PDFs
```bash
curl -X POST "http://localhost:8000/ingest/Mathematics" \
  -F "files=@/path/to/file1.pdf" \
  -F "files=@/path/to/file2.pdf"
```

### List All Documents
```bash
curl http://localhost:8000/list-documents
```

### List Documents by Topic
```bash
curl http://localhost:8000/list-documents/Mathematics
```

### Delete a Document
```bash
curl -X DELETE http://localhost:8000/delete-document/1
```

### Chat with Vector Search & LLM
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Pythagoras' theorem?", "topic": "Mathematics"}'
```
**Response:**
```json
{
  "answer": "AI response...",
  "sources": ["math_book.pdf:page 3"],
  "used_context": ["first chunk of context..."],
  "llm": "Mistral 7B"
}
```

## Notes
- Only PDF files are accepted.
- All metadata is stored in `backend/data/documents.db`.
- Uploaded PDFs are stored in `backend/data/pdfs/{topic}/`.
- Vector DB is stored in `backend/data/chroma/` (persistent).
- LLM is called locally via subprocess (llama.cpp, Mistral, etc). 