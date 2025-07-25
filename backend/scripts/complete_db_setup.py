#!/usr/bin/env python3
"""
Complete database setup script for Elimu Hub.
This script will create all necessary tables.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, SessionLocal
from app.models import document, chat, analytics
from app.auth.models import User
from sqlalchemy import text
from app.utils.logger import logger

def create_all_tables():
    """Create all database tables."""
    try:
        # Import all models to ensure they're registered
        from app.db.database import Document, Topic
        from app.models.chat import ChatSession, ChatMessage
        from app.models.analytics import APIRequest
        from app.auth.models import User
        
        # Create all tables
        from app.db.database import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("All database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def verify_tables():
    """Verify that all required tables exist."""
    required_tables = [
        'users', 'documents', 'topics', 'chat_sessions', 'chat_messages', 'api_requests'
    ]
    
    try:
        with engine.connect() as conn:
            # Get list of existing tables
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            existing_tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"Existing tables: {existing_tables}")
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            else:
                logger.info("All required tables exist")
                return True
                
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        return False

def setup_fts():
    """Set up Full-Text Search for documents."""
    try:
        with engine.connect() as conn:
            # Create FTS5 virtual table for documents
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    id,
                    filename,
                    content,
                    topic,
                    content=documents,
                    content_rowid=id
                );
            """))
            
            # Create triggers to maintain FTS index
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(rowid, filename, content, topic) 
                    VALUES (new.id, new.filename, new.content, new.topic);
                END;
            """))
            
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, filename, content, topic) 
                    VALUES('delete', old.id, old.filename, old.content, old.topic);
                END;
            """))
            
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, filename, content, topic) 
                    VALUES('delete', old.id, old.filename, old.content, old.topic);
                    INSERT INTO documents_fts(rowid, filename, content, topic) 
                    VALUES (new.id, new.filename, new.content, new.topic);
                END;
            """))
            
            conn.commit()
            logger.info("FTS5 setup completed")
            return True
            
    except Exception as e:
        logger.error(f"Error setting up FTS: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("Starting complete database setup...")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create all tables
    if not create_all_tables():
        logger.error("Failed to create tables")
        return False
    
    # Verify tables
    if not verify_tables():
        logger.error("Table verification failed")
        return False
    
    # Setup FTS
    if not setup_fts():
        logger.error("FTS setup failed")
        return False
    
    logger.info("Complete database setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
