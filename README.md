# Elimu Hub AI - Generative AI Platform

A comprehensive generative AI platform designed for Kenyan education, featuring document-based knowledge training, multiple AI interaction modes, and advanced admin management capabilities.

## 🚀 Features

### **Generative AI Capabilities**
- **Multi-Mode AI Interface**: Chat, Completion, and RAG (Retrieval-Augmented Generation)
- **Local LLM Integration**: Mistral 7B and Llama models via llama.cpp
- **API-First Design**: OpenAI-compatible endpoints for easy integration
- **Real-time Streaming**: WebSocket support for live response streaming
- **Context-Aware Responses**: Intelligent conversation management

### **Knowledge Base Management**
- **PDF Training Pipeline**: Upload and process educational documents
- **Topic-Based Organization**: Organize content by subject areas
- **Semantic Search**: Vector-based document retrieval using BGE-M3 embeddings
- **Full-Text Search**: SQLite FTS5 for fast content search
- **Automatic Processing**: Background document ingestion and embedding

### **Advanced Admin Dashboard**
- **File Upload Management**: Bulk PDF upload with progress tracking
- **Knowledge Base Overview**: Topic management and statistics
- **System Monitoring**: Health checks, analytics, and performance metrics
- **User Management**: Authentication and authorization controls
- **Training Jobs**: Background processing with status tracking

### **Security & Performance**
- **JWT Authentication**: Secure user authentication and authorization
- **Rate Limiting**: API abuse prevention
- **Caching**: Redis-based performance optimization
- **Background Jobs**: Async processing for heavy operations
- **Comprehensive Logging**: Structured logging for debugging and monitoring

## 🏗️ Architecture

```
Elimu Hub AI
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints (LLM, Admin, Chat, etc.)
│   │   ├── auth/         # Authentication system
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic (LLM, Vector Store, etc.)
│   │   └── utils/        # Utilities and helpers
│   ├── data/             # Data storage (PDFs, ChromaDB, SQLite)
│   └── scripts/          # Database migrations and utilities
└── frontend/             # Next.js frontend
    ├── src/
    │   ├── app/          # Next.js app directory
    │   ├── components/   # React components
    │   └── hooks/        # Custom React hooks
    └── public/           # Static assets
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **ChromaDB**: Vector database for embeddings
- **sentence-transformers**: BGE-M3 embedding model
- **llama.cpp**: Local LLM inference
- **Redis**: Caching and session management
- **SQLite**: Primary database with FTS5

### Frontend
- **Next.js 15**: React framework with app directory
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React 19**: Latest React features

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker** (optional)
- **Git**

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/EddMarwa/Elimu-hub-1.0.git
cd Elimu-hub-1.0
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.development .env
# Edit .env with your settings

# Run database migrations
python scripts/migrate_db.py

# Create admin user (first time only)
python scripts/create_admin.py

# Start the backend
python run.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local with your settings

# Start development server
npm run dev
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

## 🔧 Configuration

### Backend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key...` | JWT secret key |
| `LLM_MODEL_PATH` | `./models/mistral-7b.Q4_K_M.gguf` | Path to LLM model |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | Embedding model |
| `MAX_FILE_SIZE` | `52428800` | Max upload size (50MB) |
| `SIMILARITY_THRESHOLD` | `0.6` | Vector search threshold |
| `REDIS_ENABLED` | `False` | Enable Redis caching |

### Frontend Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws` | WebSocket URL |
| `NEXT_PUBLIC_ENABLE_GENERATIVE_AI` | `true` | Enable AI features |

## 📖 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Generative AI
- `POST /api/v1/llm/completions` - Text completion
- `POST /api/v1/llm/chat/completions` - Chat completion
- `POST /api/v1/llm/generate` - Simple generation
- `GET /api/v1/llm/models` - List available models

### Knowledge Base
- `POST /api/v1/ingest/{topic}` - Upload documents
- `POST /api/v1/chat` - RAG-powered chat
- `GET /api/v1/list-topics` - List topics
- `GET /api/v1/search-documents` - Search documents

### Admin (Admin Only)
- `GET /api/v1/admin/dashboard/stats` - Dashboard statistics
- `POST /api/v1/admin/upload/training-files` - Bulk file upload
- `GET /api/v1/admin/knowledge-base/overview` - Knowledge base overview
- `DELETE /api/v1/admin/knowledge-base/{topic}` - Delete topic
- `POST /api/v1/admin/knowledge-base/retrain/{topic}` - Retrain topic

## 🎯 Usage Examples

### Generative AI Chat
```javascript
// Chat completion
const response = await fetch('/api/v1/llm/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    messages: [
      {role: 'user', content: 'Explain photosynthesis'}
    ],
    max_tokens: 512,
    temperature: 0.7
  })
});
```

### Knowledge Base Upload
```javascript
// Upload training documents
const formData = new FormData();
formData.append('topic', 'Biology');
formData.append('description', 'High school biology materials');
formData.append('files', pdfFile1);
formData.append('files', pdfFile2);

const response = await fetch('/api/v1/admin/upload/training-files', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
```

### RAG Query
```javascript
// Ask questions about uploaded documents
const response = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: 'What is the process of photosynthesis?',
    topic: 'Biology'
  })
});
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password protection
- **Rate Limiting**: Request throttling (60/min, 1000/hour)
- **Input Validation**: Comprehensive request validation
- **File Upload Security**: Type and size restrictions
- **Admin Access Control**: Role-based permissions

## 🔄 Development Workflow

### Adding New Features
1. **Backend**: Add endpoints in `backend/app/api/`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Database**: Add models in `backend/app/models/`
4. **Services**: Add business logic in `backend/app/services/`

### Testing
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests (when implemented)
cd frontend
npm test
```

### Docker Deployment
```bash
# Backend
cd backend
docker-compose up --build

# Or build manually
docker build -t elimu-hub-backend .
docker run -p 8000:8000 elimu-hub-backend
```

## 📊 Admin Features

### Dashboard Overview
- **System Statistics**: Documents, topics, users, storage
- **Health Monitoring**: Database, vector store, LLM status
- **Recent Activity**: Upload history and user actions

### File Management
- **Bulk Upload**: Multiple PDF files at once
- **Topic Management**: Create, edit, delete topics
- **Retraining**: Rebuild vector embeddings
- **Storage Monitoring**: Track disk usage

### User Management
- **Authentication Control**: User registration and login
- **Admin Privileges**: Role-based access control
- **Activity Tracking**: User behavior analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and commit: `git commit -m "Add new feature"`
4. Push to the branch: `git push origin feature/new-feature`
5. Create a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Add tests for new features
- Update documentation
- Ensure proper error handling

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mistral AI** for the Mistral 7B model
- **BGE Team** for the BGE-M3 embedding model
- **ChromaDB** for vector database capabilities
- **FastAPI** and **Next.js** communities

## 📞 Support

For support, email support@elimuhub.ai or open an issue on GitHub.

---

**Elimu Hub AI** - Transforming education through generative AI technology.