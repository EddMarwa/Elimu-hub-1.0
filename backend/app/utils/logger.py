import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logger(name: str = "elimu_hub") -> logging.Logger:
    """Setup and configure logger for the application."""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

# Create default logger
logger = setup_logger() 