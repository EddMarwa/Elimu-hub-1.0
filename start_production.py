#!/usr/bin/env python3
"""
Production startup script for Elimu Hub
Handles database migration and server startup seamlessly
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path

def backup_existing_database():
    """Backup existing database if it exists"""
    db_path = Path("minimal_kb.db")
    if db_path.exists():
        backup_path = Path(f"minimal_kb_backup_{int(__import__('time').time())}.db")
        shutil.copy2(db_path, backup_path)
        print(f"📦 Backed up existing database to {backup_path}")
        return backup_path
    return None

def migrate_database():
    """Migrate database schema to include new columns"""
    db_path = Path("minimal_kb.db")
    
    if not db_path.exists():
        print("📊 No existing database found, will create new one")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if page_number column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'page_number' not in columns:
            print("🔄 Adding page_number column to documents table...")
            cursor.execute("ALTER TABLE documents ADD COLUMN page_number INTEGER DEFAULT NULL")
            
        if 'chat_session_id' not in columns:
            print("🔄 Adding chat_session_id column to documents table...")
            cursor.execute("ALTER TABLE documents ADD COLUMN chat_session_id TEXT")
            
        conn.commit()
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        print("🔄 Will recreate database with new schema")
        conn.close()
        # Remove old database and let the server create a new one
        db_path.unlink()
        return
    
    conn.close()

def setup_environment():
    """Setup environment variables and check requirements"""
    # Check for GROQ API key
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not set. AI responses will use fallback mode.")
        print("   Set GROQ_API_KEY environment variable for full AI functionality.")
    else:
        print("✅ GROQ_API_KEY found - AI responses enabled")
    
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("data/pdfs").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    print("📁 Required directories created/verified")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Elimu Hub server...")
    
    try:
        import uvicorn
        from minimal_server import app
        
        # Run server with production settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🎓 Elimu Hub - Production Startup")
    print("=" * 40)
    
    # Setup environment
    setup_environment()
    
    # Backup and migrate database
    backup_existing_database()
    migrate_database()
    
    # Start server
    start_server()
