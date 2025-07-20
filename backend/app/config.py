import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PDF_DIR = DATA_DIR / "pdfs"
    CHROMA_DIR = DATA_DIR / "chroma"
    DB_PATH = DATA_DIR / "documents.db"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    
    # Authentication & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Embedding settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "250"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "40"))
    
    # LLM settings
    LLM_MODEL_PATH: str = os.getenv("LLM_MODEL_PATH", "./models/mistral-7b.Q4_K_M.gguf")
    LLAMA_CPP_PATH: str = os.getenv("LLAMA_CPP_PATH", "/usr/local/bin/llama.cpp")
    LLM_NAME: str = os.getenv("LLM_NAME", "Mistral 7B")
    
    # API settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    ALLOWED_EXTENSIONS: list = [".pdf"]
    
    # Security
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # Similarity search
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Redis Cache Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "3600"))  # 1 hour default
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "False").lower() == "true"
    
    def __init__(self):
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.PDF_DIR.mkdir(exist_ok=True)
        self.CHROMA_DIR.mkdir(exist_ok=True)
        
        # Create logs directory
        log_dir = Path(self.LOG_FILE).parent
        log_dir.mkdir(exist_ok=True)

settings = Settings() 