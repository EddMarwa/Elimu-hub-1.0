#!/usr/bin/env python3
"""
Debug database content to see what's being stored
"""

import sqlite3
from pathlib import Path

def debug_database():
    """Check what content is actually stored in the database"""
    db_path = Path("data/documents.db")
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("🔍 Database Content Analysis")
    print("=" * 30)
    
    # Check documents table
    cursor.execute("SELECT id, filename, topic, LENGTH(content), SUBSTR(content, 1, 100) FROM documents")
    docs = cursor.fetchall()
    
    print(f"\n📚 Found {len(docs)} documents:")
    for doc_id, filename, topic, content_length, content_preview in docs:
        print(f"\n📄 Document {doc_id}: {filename}")
        print(f"   Topic: {topic}")
        print(f"   Content Length: {content_length} characters")
        print(f"   Preview: {content_preview}...")
        
        if content_length == 0:
            print("   ⚠️  WARNING: Empty content!")
    
    # Test search query directly on database
    print(f"\n🔍 Testing direct database search for 'derivative':")
    cursor.execute("""
        SELECT filename, topic, SUBSTR(content, 1, 200) 
        FROM documents 
        WHERE LOWER(content) LIKE '%derivative%'
    """)
    
    results = cursor.fetchall()
    print(f"   Found {len(results)} matches:")
    for filename, topic, content_snippet in results:
        print(f"   📄 {filename} ({topic}): {content_snippet}...")
    
    # Test search for other terms
    test_terms = ['calculus', 'biology', 'cell', 'function']
    for term in test_terms:
        cursor.execute("""
            SELECT COUNT(*) FROM documents 
            WHERE LOWER(content) LIKE ?
        """, (f'%{term}%',))
        count = cursor.fetchone()[0]
        print(f"   🔍 '{term}': {count} matches")
    
    conn.close()

if __name__ == "__main__":
    debug_database()
