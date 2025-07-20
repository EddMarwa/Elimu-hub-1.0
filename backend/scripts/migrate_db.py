#!/usr/bin/env python3
"""
Database migration script for Elimu Hub.
Usage: python scripts/migrate_db.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, Base
from app.auth.models import User
from app.models.chat import ChatSession, ChatMessage
from app.utils.logger import logger

def run_migrations():
    """Run database migrations."""
    logger.info("Starting database migration...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database migration completed successfully")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"Available tables: {', '.join(tables)}")
        
        # Verify required tables exist
        required_tables = ['users', 'documents', 'chat_sessions', 'chat_messages']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"Missing tables: {', '.join(missing_tables)}")
            return False
        
        logger.info("All required tables are present")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def check_data_integrity():
    """Check data integrity after migration."""
    logger.info("Checking data integrity...")
    
    try:
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        
        # Check user count
        user_count = db.query(User).count()
        logger.info(f"Total users: {user_count}")
        
        # Check document count
        from app.db.database import Document
        doc_count = db.query(Document).count()
        logger.info(f"Total documents: {doc_count}")
        
        # Check chat sessions count
        session_count = db.query(ChatSession).count()
        logger.info(f"Total chat sessions: {session_count}")
        
        # Check chat messages count
        message_count = db.query(ChatMessage).count()
        logger.info(f"Total chat messages: {message_count}")
        
        db.close()
        logger.info("Data integrity check completed")
        return True
        
    except Exception as e:
        logger.error(f"Data integrity check failed: {e}")
        return False

def main():
    """Main migration function."""
    print("Elimu Hub - Database Migration")
    print("=" * 40)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migration failed")
        return
    
    # Check data integrity
    if not check_data_integrity():
        print("❌ Data integrity check failed")
        return
    
    print("✅ Database migration completed successfully!")

if __name__ == "__main__":
    main() 