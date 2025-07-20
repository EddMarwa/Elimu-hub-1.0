#!/usr/bin/env python3
"""
Final database migration script for Elimu Hub backend.
This script ensures all tables are created and properly indexed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base, SessionLocal
from app.auth.models import User
from app.models.chat import ChatSession, ChatMessage
from app.models.analytics import APIRequest, UserActivity, SystemMetrics
from app.models.document import Document
from app.db.fts import setup_fts
from app.utils.logger import logger
from sqlalchemy import text

def run_migration():
    """Run the final database migration."""
    logger.info("Starting final database migration...")
    
    try:
        # Create all tables
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
        
        # Setup FTS
        logger.info("Setting up full-text search...")
        setup_fts()
        logger.info("Full-text search setup complete")
        
        # Create indexes for better performance
        logger.info("Creating database indexes...")
        with engine.connect() as conn:
            # Analytics indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_api_requests_user_id 
                ON api_requests(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_api_requests_created_at 
                ON api_requests(created_at)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_activities_user_id 
                ON user_activities(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_user_activities_created_at 
                ON user_activities(created_at)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_system_metrics_created_at 
                ON system_metrics(created_at)
            """))
            
            # Chat indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id 
                ON chat_sessions(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id 
                ON chat_messages(session_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp 
                ON chat_messages(timestamp)
            """))
            
            # Document indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_user_id 
                ON documents(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at 
                ON documents(uploaded_at)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_documents_file_type 
                ON documents(file_type)
            """))
            
            conn.commit()
        
        logger.info("Database indexes created successfully")
        
        # Verify all tables exist
        logger.info("Verifying table structure...")
        with engine.connect() as conn:
            tables = [
                "users", "documents", "chat_sessions", "chat_messages",
                "api_requests", "user_activities", "system_metrics"
            ]
            
            for table in tables:
                result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                if result.fetchone():
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.error(f"✗ Table '{table}' missing!")
                    return False
        
        logger.info("All tables verified successfully")
        
        # Check for admin user
        db = SessionLocal()
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            logger.warning("No admin user found. Please create one using create_admin.py")
        else:
            logger.info(f"Admin user found: {admin_user.email}")
        
        db.close()
        
        logger.info("Final database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1) 