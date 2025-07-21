#!/usr/bin/env python3
"""
Production startup script for Elimu Hub backend.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.enhanced_logger import setup_logging, logger
from app.config import settings

def check_dependencies():
    """Check if all required dependencies are available."""
    logger.info("Checking dependencies...")
    
    # Check if data directories exist
    required_dirs = [
        settings.DATA_DIR,
        settings.PDF_DIR,
        settings.CHROMA_DIR,
        Path("logs")
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ensured: {dir_path}")
    
    return True

def setup_database():
    """Set up the database if needed."""
    logger.info("Setting up database...")
    
    try:
        # Import here to avoid circular imports
        from app.db.database import engine, Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created/verified")
        
        return True
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def run_migrations():
    """Run database migrations."""
    logger.info("Running database migrations...")
    
    try:
        migration_script = Path("scripts/migrate_db.py")
        if migration_script.exists():
            subprocess.run([sys.executable, str(migration_script)], check=True)
            logger.info("✓ Database migrations completed")
        else:
            logger.warning("Migration script not found, skipping")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e}")
        return False

async def startup_checks():
    """Perform all startup checks."""
    logger.info("Starting Elimu Hub Backend...")
    logger.info(f"Environment: {os.getenv('NODE_ENV', 'development')}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")
    
    # Perform checks
    if not check_dependencies():
        logger.error("Dependency check failed")
        sys.exit(1)
    
    if not setup_database():
        logger.error("Database setup failed")
        sys.exit(1)
    
    if not run_migrations():
        logger.error("Database migrations failed")
        sys.exit(1)
    
    logger.info("✓ All startup checks passed")

def main():
    """Main entry point."""
    # Setup logging
    setup_logging(settings.LOG_LEVEL)
    
    # Run startup checks
    asyncio.run(startup_checks())
    
    # Start the server
    logger.info("Starting FastAPI server...")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True,
            workers=1 if settings.DEBUG else 4
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
