from sqlalchemy import event, text
from app.db.database import engine
from app.utils.logger import logger

# FTS5 table for document content
CREATE_FTS_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
    doc_id UNINDEXED,
    topic,
    file_name,
    content
);
"""

# Trigger to keep FTS table in sync with documents
CREATE_INSERT_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS document_ai AFTER INSERT ON documents BEGIN
    INSERT INTO document_fts(doc_id, topic, file_name, content)
    VALUES (new.id, new.topic, new.file_name, '');
END;
"""

CREATE_DELETE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS document_ad AFTER DELETE ON documents BEGIN
    DELETE FROM document_fts WHERE doc_id = old.id;
END;
"""

CREATE_UPDATE_TRIGGER = """
CREATE TRIGGER IF NOT EXISTS document_au AFTER UPDATE ON documents BEGIN
    UPDATE document_fts SET topic = new.topic, file_name = new.file_name WHERE doc_id = new.id;
END;
"""

def setup_fts():
    """Create FTS5 table and triggers if not exist."""
    with engine.connect() as conn:
        logger.info("Setting up FTS5 for documents...")
        conn.execute(text(CREATE_FTS_TABLE))
        conn.execute(text(CREATE_INSERT_TRIGGER))
        conn.execute(text(CREATE_DELETE_TRIGGER))
        conn.execute(text(CREATE_UPDATE_TRIGGER))
        logger.info("FTS5 setup complete.")

def insert_document_content(doc_id: int, content: str):
    """Insert or update document content in FTS table."""
    with engine.connect() as conn:
        conn.execute(text("UPDATE document_fts SET content = :content WHERE doc_id = :doc_id"), {"content": content, "doc_id": doc_id})

def search_documents(query: str, limit: int = 10):
    """Search documents using FTS5."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT doc_id, topic, file_name, snippet(document_fts, 3, '<b>', '</b>', '...', 10) as snippet
            FROM document_fts
            WHERE document_fts MATCH :query
            LIMIT :limit
        """), {"query": query, "limit": limit})
        return [dict(row) for row in result] 