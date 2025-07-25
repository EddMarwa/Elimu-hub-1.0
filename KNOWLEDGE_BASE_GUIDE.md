# 📚 Elimu Hub Knowledge Base Guide

Your Elimu Hub platform is now **fully operational**! Here's how to build and use your PDF-based knowledge base with RAG capabilities.

## 🎯 What You Can Do

### ✅ **PDF Knowledge Base**
- Upload PDF documents organized by topics
- Automatic text extraction and chunking
- Vector embeddings using BGE-M3 model
- Full-text search capabilities

### ✅ **RAG-Based Q&A**
- Ask questions about uploaded documents
- Get contextual responses using retrieved content
- Multiple LLM provider support (OpenRouter, Groq, HuggingFace)

### ✅ **Topic Organization**
- Organize content by subjects (Biology, Math, History, etc.)
- Topic-specific searches
- Bulk document uploads per topic

## 🚀 Quick Start Guide

### 1. **Access Your Platform**
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Credentials**: 
  - Email: admin1@elimuhub.com
  - Username: Admin123#
  - Password: Admin@2025#

### 2. **Upload PDF Documents**

#### Option A: Using API Directly
```bash
# First, get an authentication token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin1@elimuhub.com", "password": "Admin@2025#"}'

# Upload a PDF document
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "topic_id=1" \
  -F "file=@your_document.pdf"
```

#### Option B: Using the Web Interface
1. Visit http://localhost:8000/docs
2. Use the `/api/v1/auth/login` endpoint to get a token
3. Use the `/api/v1/admin/upload/training-files` endpoint to upload PDFs

### 3. **Create Topics**

Topics help organize your documents by subject area:

```bash
# Create a new topic
curl -X POST "http://localhost:8000/api/v1/topics" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Biology",
    "description": "High school biology materials"
  }'
```

Common topics you might create:
- **Biology** - Life sciences, genetics, ecology
- **Mathematics** - Algebra, calculus, geometry
- **Physics** - Mechanics, thermodynamics, optics
- **Chemistry** - Organic, inorganic, physical chemistry
- **History** - World history, local history
- **Literature** - Novels, poetry, literary analysis

### 4. **Bulk Upload PDFs by Topic**

Upload multiple PDFs at once for a specific topic:

```bash
curl -X POST "http://localhost:8000/api/v1/admin/upload/training-files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "topic=Biology" \
  -F "description=Grade 12 Biology textbooks" \
  -F "files=@biology_chapter1.pdf" \
  -F "files=@biology_chapter2.pdf" \
  -F "files=@biology_chapter3.pdf"
```

### 5. **Ask Questions (RAG)**

Once documents are uploaded, you can ask questions:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is photosynthesis and how does it work?",
    "topic": "Biology",
    "max_tokens": 500
  }'
```

## 🔧 Advanced Features

### **Search Capabilities**

#### 1. **Vector Similarity Search**
Find documents similar to your query using AI embeddings:

```bash
curl -X GET "http://localhost:8000/api/v1/search?query=cell+division&topic=Biology&limit=5"
```

#### 2. **Full-Text Search**
Fast keyword search across all documents:

```bash
curl -X GET "http://localhost:8000/api/v1/search/advanced?query=mitochondria&file_type=pdf"
```

### **Admin Features**

#### 1. **Knowledge Base Overview**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/knowledge-base/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 2. **Retrain Topic Embeddings**
If you add new documents, rebuild the vector embeddings:

```bash
curl -X POST "http://localhost:8000/api/v1/admin/knowledge-base/retrain/Biology" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. **System Statistics**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/dashboard/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 How It Works

### **Document Processing Pipeline**
1. **PDF Upload** → Text extraction using PyMuPDF
2. **Text Chunking** → Split into 250-word chunks with 40-word overlap
3. **Embeddings** → Generate vectors using BGE-M3 model
4. **Storage** → Store in ChromaDB vector database
5. **Indexing** → Create full-text search index

### **RAG Query Pipeline**
1. **Question** → User asks a question
2. **Embedding** → Convert question to vector
3. **Search** → Find similar document chunks
4. **Context** → Retrieve relevant text passages
5. **LLM** → Generate answer using context
6. **Response** → Return contextual answer

## 🎯 Best Practices

### **Document Organization**
- Use clear, descriptive topic names
- Keep documents focused on specific subjects
- Upload high-quality, text-based PDFs
- Avoid scanned images without OCR

### **Optimal PDF Formats**
- ✅ Text-based PDFs (searchable)
- ✅ Academic papers and textbooks
- ✅ Educational materials
- ❌ Scanned images without OCR
- ❌ PDFs with complex layouts

### **Question Asking**
- Be specific in your questions
- Reference the topic if you know it
- Ask one concept per question
- Use clear, educational language

## 🔌 LLM Configuration

Configure different LLM providers by setting environment variables:

### **OpenRouter (Recommended)**
```env
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=qwen/qwen-2.5-72b-instruct
```

### **Groq (Fast)**
```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=mixtral-8x7b-32768
```

### **HuggingFace (Free)**
```env
HUGGINGFACE_API_KEY=your_hf_key
HUGGINGFACE_MODEL=HuggingFaceH4/zephyr-7b-beta
```

## 📁 File Structure

Your knowledge base is stored in:
```
backend/data/
├── documents.db          # SQLite database
├── chroma/              # Vector embeddings
└── pdfs/               # Original PDF files
    ├── Biology/
    ├── Mathematics/
    └── Physics/
```

## 🔍 Example Workflows

### **Workflow 1: Building a Biology Knowledge Base**
1. Create "Biology" topic
2. Upload textbook PDFs (chapters 1-20)
3. Wait for processing (5-10 minutes)
4. Ask questions like:
   - "Explain cellular respiration"
   - "What are the stages of mitosis?"
   - "How do enzymes work?"

### **Workflow 2: Multi-Subject Study Platform**
1. Create topics: Math, Physics, Chemistry
2. Upload subject-specific PDFs
3. Use topic-specific searches
4. Ask comparative questions across subjects

### **Workflow 3: Research Assistant**
1. Upload research papers by topic
2. Use advanced search to find specific concepts
3. Ask for summaries and explanations
4. Generate study notes from multiple sources

## 🚨 Troubleshooting

### **Common Issues**

#### "No relevant documents found"
- Check if PDFs were uploaded successfully
- Verify topic names match
- Try broader search terms

#### "LLM API Error"
- Check your API keys in .env file
- Verify internet connection
- Try a different LLM provider

#### "Upload failed"
- Check file size (max 50MB)
- Ensure file is a valid PDF
- Verify disk space

### **Logs and Debugging**
- Check logs: `backend/logs/app.log`
- API documentation: http://localhost:8000/docs
- Database browser: Use SQLite browser for `data/documents.db`

## 🎉 You're Ready!

Your Elimu Hub platform is now ready to use! Start by:

1. 📚 **Upload your first PDF documents**
2. 🏷️ **Organize them by topics** 
3. ❓ **Ask your first questions**
4. 🔍 **Explore the search capabilities**

The system will automatically process your documents and make them searchable through AI-powered RAG queries. Each uploaded PDF becomes part of your growing knowledge base!

---

**Happy Learning with Elimu Hub! 🚀📚**
