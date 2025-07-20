# Elimu Hub Offline AI Backend

A modular FastAPI backend for an offline AI educational system. Supports topic-specific PDF ingestion, semantic search, and local LLM-powered chat.

## Features
- Upload and ingest topic-specific PDFs (chunk, embed, and store by topic)
- Query by topic: retrieves relevant context, or returns "insufficient knowledge" if match is weak
- Add new topics anytime by re-running PDF ingestion
- Local, persistent vector database (ChromaDB)
- Local LLM (Mistral 7B GGUF or Llama 3 8B via llama.cpp)
- Efficient, modular, and memory-friendly

## Project Structure
```
├── app/
│   ├── api/
│   │   ├── chat.py
│   │   └── ingest.py
│   ├── services/
│   │   ├── pdf_ingestor.py
│   │   ├── vector_store.py
│   │   └── chat_service.py
│   ├── main.py
│   └── config.py
├── data/           # Stores PDFs and ChromaDB files
└── requirements.txt
```

## Requirements
- Python 3.9+
- [ChromaDB](https://docs.trychroma.com/)
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
- [sentence-transformers](https://www.sbert.net/)
- [langchain](https://python.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp) (for local LLM)

## Setup
1. **Clone the repo and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. **Download your LLM model (GGUF) and set the path in `app/config.py`.**
3. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
### Ingest PDFs
- `POST /ingest/{topic}`
- Upload one or more PDFs for a topic. Chunks, embeds, and stores them in ChromaDB under the topic collection.

### Chat
- `POST /chat`
- JSON body: `{ "question": "...", "topic": "..." }`
- Returns an answer based on the topic's knowledge base. If no relevant info (similarity < 0.6), returns "I have insufficient knowledge on this topic."

## Adding Topics
- Just re-run the `/ingest/{topic}` endpoint with new PDFs. No retraining required.

## Data Persistence
- All embeddings and PDFs are stored in the `data/` directory. ChromaDB persists between restarts.

## Notes
- Designed for local/offline use. No cloud dependencies.
- Efficient memory usage: no large in-memory loads.
- LLM is called via subprocess using llama.cpp for maximum compatibility.

---

For more details, see the code in `app/`.