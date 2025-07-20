# Elimu Hub Backend

A FastAPI-based document management and chat system with RAG (Retrieval-Augmented Generation) capabilities.

## Features

- **Document Management**: Upload, store, and manage PDF documents by topic
- **RAG Chat System**: Ask questions and get AI-powered answers based on uploaded documents
- **Chat History**: Persistent conversation history with session management
- **Vector Search**: Semantic search using ChromaDB and BGE-M3 embeddings
- **Full-Text Search**: Fast document search using SQLite FTS5
- **Caching**: Redis-based caching for improved performance
- **Local LLM Integration**: Support for local LLM models via llama.cpp
- **Background Jobs**: Async processing for large files and long-running tasks
- **RESTful API**: Complete API with automatic documentation
- **Authentication**: JWT-based user authentication and authorization
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Logging**: Comprehensive logging system
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your settings, especially SECRET_KEY
   ```

3. **Run database migration**:
   ```bash
   python scripts/migrate_db.py
   ```

4. **Create admin user** (first time only):
   ```bash
   python scripts/create_admin.py
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Or build manually**:
   ```bash
   docker build -t elimu-hub-backend .
   docker run -p 8000:8000 elimu-hub-backend
   ```

## Authentication

The API uses JWT-based authentication. All protected endpoints require a valid Bearer token.

### Getting Started with Authentication

1. **Register a new user**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "username": "testuser", "password": "password123"}'
   ```

2. **Login to get access token**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
   ```

3. **Use the token for authenticated requests**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/ingest/Mathematics" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -F "files=@document.pdf"
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token
- `GET /api/v1/auth/me` - Get current user profile (authenticated)
- `POST /api/v1/auth/logout` - Logout user (authenticated)

### Document Management (Authenticated)
- `POST /api/v1/ingest/{topic}` - Upload PDF documents to a topic
- `GET /api/v1/list-documents` - List all documents
- `GET /api/v1/list-documents/{topic}` - List documents by topic
- `DELETE /api/v1/delete-document/{id}` - Delete a document

### Chat (Authenticated)
- `POST /api/v1/chat` - Ask questions about uploaded documents (with session support)

### Chat History (Authenticated)
- `POST /api/v1/chat/sessions` - Create a new chat session
- `GET /api/v1/chat/sessions` - List all chat sessions
- `GET /api/v1/chat/sessions/{session_id}` - Get chat history for a session
- `DELETE /api/v1/chat/sessions/{session_id}` - Delete a chat session
- `POST /api/v1/chat/sessions/{session_id}/messages` - Add message to session

### Job Management (Authenticated)
- `GET /api/v1/jobs` - List all background jobs
- `GET /api/v1/jobs/{job_id}` - Get job status
- `DELETE /api/v1/jobs/{job_id}` - Cancel a job
- `POST /api/v1/jobs/cleanup` - Clean up completed jobs (admin only)

### Search (Authenticated)
- `GET /api/v1/search-documents?q=your+query` - Full-text search for documents (content and metadata)

### Example: Search Documents

```bash
curl -X GET "http://localhost:8000/api/v1/search-documents?q=calculus" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Analytics (Admin Only)
- `GET /api/v1/analytics/summary?hours=24` - Get analytics summary for the last N hours
- `GET /api/v1/analytics/system-metrics` - Get current system metrics (CPU, memory, disk)
- `GET /api/v1/analytics/health` - Health check for analytics service

### Example: Get Analytics Summary

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary?hours=24" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Chat Sessions

The chat system now supports persistent conversations:

1. **Start a new conversation**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is calculus?", "topic": "Mathematics"}'
   ```

2. **Continue in the same session**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question": "Can you explain derivatives?", "topic": "Mathematics", "session_id": 1}'
   ```

3. **View chat history**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/chat/sessions/1" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Background Jobs

The system includes a background job queue for processing large files and long-running tasks:

- **Job Status**: pending, running, completed, failed, cancelled
- **Job Monitoring**: Track progress and status of background tasks
- **Job Management**: Cancel pending jobs, cleanup completed jobs

## Configuration

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `False` | Debug mode |
| `SECRET_KEY` | `your-secret-key...` | JWT secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |
| `RATE_LIMIT_PER_MINUTE` | `60` | Requests per minute |
| `RATE_LIMIT_PER_HOUR` | `1000` | Requests per hour |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_FILE_SIZE` | `52428800` | Max file size (50MB) |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Embedding model |
| `LLM_MODEL_PATH` | `./models/mistral-7b.Q4_K_M.gguf` | LLM model path |
| `SIMILARITY_THRESHOLD` | `0.6` | Similarity threshold |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_CACHE_TTL` | `3600` | Cache TTL in seconds |
| `REDIS_ENABLED` | `False` | Enable Redis caching |

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **Rate Limiting**: Per-minute and per-hour rate limits
- **Input Validation**: Comprehensive input validation
- **CORS Protection**: Configurable CORS settings
- **File Upload Security**: File type and size validation

## Testing

Run tests:
```bash
pytest tests/
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── auth/          # Authentication models and utilities
│   ├── db/            # Database models and connection
│   ├── middleware/    # Custom middleware (rate limiting)
│   ├── models/        # Data models (chat, etc.)
│   ├── services/      # Business logic services
│   ├── utils/         # Utilities (logging, etc.)
│   ├── config.py      # Configuration settings
│   └── main.py        # FastAPI application
├── data/              # Data storage (PDFs, vectors, DB)
├── logs/              # Application logs
├── scripts/           # Utility scripts
├── tests/             # Test files
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
├── requirements.txt   # Python dependencies
└── run.py            # Application runner
```

## Development

### Adding New Features

1. **API Endpoints**: Add to `app/api/`
2. **Services**: Add to `app/services/`
3. **Database Models**: Add to `app/db/` or `app/models/`
4. **Configuration**: Add to `app/config.py`

### Authentication in New Endpoints

To protect an endpoint with authentication:

```python
from app.auth.dependencies import get_current_active_user
from app.auth.models import User

@router.get("/protected-endpoint")
async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}!"}
```

### Background Jobs

To create a background job:

```python
from app.services.job_queue import job_queue
import uuid

def process_large_file(file_path):
    # Your processing logic here
    pass

# Submit job
job_id = str(uuid.uuid4())
job_queue.submit_job(job_id, process_large_file, (file_path,))
```

### Logging

The application uses structured logging. Logs are written to both console and file:

```python
from app.utils.logger import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

## Database Management

### Running Migrations

```bash
python scripts/migrate_db.py
```

### Creating Admin User

```bash
python scripts/create_admin.py
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change `PORT` in environment variables
2. **Authentication errors**: Check `SECRET_KEY` and token expiration
3. **Rate limiting**: Check rate limit settings
4. **File upload fails**: Check `MAX_FILE_SIZE` setting
5. **LLM not working**: Verify `LLM_MODEL_PATH` and `LLAMA_CPP_PATH`
6. **Memory issues**: Reduce `CHUNK_SIZE` or `TOP_K_RESULTS`
7. **Database errors**: Run migration script and check logs

### Logs

Check logs in `logs/app.log` for detailed error information.

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use proper logging
5. Follow PEP 8 style guidelines
6. Ensure authentication is properly implemented for new endpoints
7. Add database migrations for schema changes 

### Upload Progress (WebSocket)
- `WS /ws/upload-progress` - Real-time upload progress tracking
- Requires authentication via WebSocket headers

### Advanced Search
- `GET /api/v1/search/advanced` - Advanced search with filtering, sorting, and pagination
- `GET /api/v1/search/facets` - Get search facets for filtering

### Export/Import (Admin Only)
- `GET /api/v1/export/documents?format=json|csv` - Export all documents
- `GET /api/v1/export/chat-history?format=json|csv` - Export chat history
- `POST /api/v1/import/documents` - Import documents from JSON file
- `GET /api/v1/export/system-stats` - Export system statistics

### Example: Advanced Search

```bash
curl -X GET "http://localhost:8000/api/v1/search/advanced?query=python&page=1&page_size=10&sort_by=relevance&file_type=pdf" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Example: Export Documents

```bash
curl -X GET "http://localhost:8000/api/v1/export/documents?format=csv" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  --output documents_export.csv
``` 