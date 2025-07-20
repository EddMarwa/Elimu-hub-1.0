import pytest
from app.config import settings

def test_settings_initialization():
    """Test that settings are properly initialized."""
    assert settings.BASE_DIR.exists()
    assert settings.DATA_DIR.exists()
    assert settings.PDF_DIR.exists()
    assert settings.CHROMA_DIR.exists()

def test_embedding_settings():
    """Test embedding model settings."""
    assert settings.EMBEDDING_MODEL == "BAAI/bge-m3"
    assert settings.CHUNK_SIZE == 250
    assert settings.CHUNK_OVERLAP == 40

def test_api_settings():
    """Test API settings."""
    assert settings.MAX_FILE_SIZE > 0
    assert ".pdf" in settings.ALLOWED_EXTENSIONS
    assert len(settings.CORS_ORIGINS) > 0

def test_search_settings():
    """Test search settings."""
    assert 0 < settings.SIMILARITY_THRESHOLD < 1
    assert settings.TOP_K_RESULTS > 0

def test_server_settings():
    """Test server settings."""
    assert settings.HOST in ["0.0.0.0", "127.0.0.1", "localhost"]
    assert 1024 <= settings.PORT <= 65535
    assert isinstance(settings.DEBUG, bool) 