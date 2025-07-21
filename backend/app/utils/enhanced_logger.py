import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Set up comprehensive logging for the application.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_path = log_dir / log_file
    else:
        file_path = log_dir / "app.log"
        
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_file_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_file_handler)
    
    return logger

def log_request(request, response_time: float = None):
    """Log HTTP requests."""
    logger = logging.getLogger("request")
    method = request.method
    url = request.url
    client_ip = request.client.host
    
    log_msg = f"{method} {url} - {client_ip}"
    if response_time:
        log_msg += f" - {response_time:.3f}s"
        
    logger.info(log_msg)

def log_error(error: Exception, context: str = ""):
    """Log errors with context."""
    logger = logging.getLogger("error")
    error_msg = f"{context}: {str(error)}"
    logger.error(error_msg, exc_info=True)

# Initialize default logger
logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))
