from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import ingest, documents, chat, auth, chat_history, jobs, ws_chat, search, analytics, upload_progress, advanced_search, export_import
from app.config import settings
from app.utils.logger import logger
from app.middleware.rate_limit import rate_limit_middleware
from app.services.job_queue import job_queue
from app.db.fts import setup_fts
from app.services.analytics import analytics
import time

app = FastAPI(
    title="Elimu Hub Document Management & Chat API",
    description="A RAG-based document management and chat system for educational content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    # Log to analytics
    try:
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = request.state.user.id
        
        analytics.log_api_request(
            user_id=user_id,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            response_time=process_time,
            user_agent=request.headers.get("user-agent"),
            ip_address=request.client.host if request.client else None
        )
    except Exception as e:
        logger.error(f"Error logging analytics: {e}")
    
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(chat_history.router, prefix="/api/v1/chat", tags=["chat-history"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(ws_chat.router, tags=["ws-chat"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(upload_progress.router, tags=["upload-progress"])
app.include_router(advanced_search.router, prefix="/api/v1", tags=["advanced-search"])
app.include_router(export_import.router, prefix="/api/v1", tags=["export-import"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Elimu Hub API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "timestamp": time.time()}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Elimu Hub API...")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    
    # Start the job queue
    job_queue.start()
    logger.info("Job queue started")
    
    # Setup FTS
    setup_fts()
    logger.info("FTS5 for documents is ready")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Elimu Hub API...")
    
    # Stop the job queue
    job_queue.stop()
    logger.info("Job queue stopped") 