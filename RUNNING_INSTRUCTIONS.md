# 🎓 Elimu Hub - Running Instructions

## 📋 Quick Start Guide

### **Option 1: One-Click Startup (Easiest)**
```powershell
# Navigate to project root
cd C:\Users\Edd\Documents\Github\Elimu-hub-1.0

# Run the complete startup script
.\start_app.ps1
```

### **Option 2: Individual Scripts**
```powershell
# Terminal 1 - Backend
.\start_backend.ps1

# Terminal 2 - Frontend  
.\start_frontend.ps1
```

### **Option 3: Manual Startup**

#### **Backend Server:**
```powershell
cd C:\Users\Edd\Documents\Github\Elimu-hub-1.0
.venv\Scripts\activate
cd backend
python minimal_server.py
```

#### **Frontend Server:**
```powershell
cd C:\Users\Edd\Documents\Github\Elimu-hub-1.0\frontend
npm run dev
```

---

## 🌐 **Access URLs**

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |

---

## 🔧 **Troubleshooting**

### **Port Already in Use:**
```powershell
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
taskkill /PID <ProcessID> /F
```

### **Python Environment Issues:**
```powershell
# Recreate virtual environment
Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
```

### **Node.js Issues:**
```powershell
# Clear npm cache and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

---

## 📦 **Dependencies**

### **Backend Requirements:**
- fastapi
- uvicorn
- python-multipart
- pymupdf
- python-jose[cryptography]
- requests
- python-dotenv

### **Frontend Requirements:**
- Next.js 15.4.1
- React 18
- TypeScript
- Tailwind CSS

---

## 🔑 **Environment Setup**

### **Required Environment Variables:**
Create a `.env` file in the backend directory:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

---

## ✅ **Verification Steps**

1. **Backend Health Check:**
   - Visit: http://localhost:8000/docs
   - Should see FastAPI documentation

2. **Frontend Health Check:**
   - Visit: http://localhost:3000
   - Should see Elimu Hub interface

3. **Full System Test:**
   - Upload a PDF through the sidebar
   - Ask a question in the chat
   - Verify AI responses with page references

---

## 🎯 **Features Implemented**

- ✅ PDF document upload and processing
- ✅ AI-powered chat with page references
- ✅ Session-based document management
- ✅ Responsive design for mobile/desktop
- ✅ Reference styling (italic green text)
- ✅ Single upload interface in sidebar
- ✅ Adaptive chat interface

---

## 📞 **Support**

If you encounter issues:
1. Check the terminal output for error messages
2. Verify all dependencies are installed
3. Ensure ports 3000 and 8000 are available
4. Check that GROQ_API_KEY is properly set

---

## 🚀 **Production Deployment**

For production deployment, update the environment variables and use:
```bash
# Backend
uvicorn minimal_server:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
npm start
```
