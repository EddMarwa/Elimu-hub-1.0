import redis
import json
import pickle
from typing import Any, Optional
from app.config import settings
from app.utils.logger import logger

class RedisCache:
    def __init__(self):
        self.redis_client = None
        self.enabled = settings.REDIS_ENABLED
        
        if self.enabled:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None
    
    def _get_key(self, prefix: str, key: str) -> str:
        """Generate a cache key with prefix."""
        return f"elimu_hub:{prefix}:{key}"
    
    def get(self, prefix: str, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._get_key(prefix, key)
            value = self.redis_client.get(cache_key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, prefix: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(prefix, key)
            serialized_value = pickle.dumps(value)
            ttl = ttl or settings.REDIS_CACHE_TTL
            self.redis_client.setex(cache_key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, prefix: str, key: str) -> bool:
        """Delete a value from cache."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(prefix, key)
            self.redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear_prefix(self, prefix: str) -> bool:
        """Clear all keys with a specific prefix."""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            pattern = self._get_key(prefix, "*")
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis clear prefix error: {e}")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status from cache."""
        return self.get("job", job_id)
    
    def set_job_status(self, job_id: str, status: dict, ttl: int = 300) -> bool:
        """Set job status in cache (5 minutes TTL)."""
        return self.set("job", job_id, status, ttl)
    
    def get_document_list(self, topic: Optional[str] = None) -> Optional[list]:
        """Get document list from cache."""
        key = f"docs_{topic}" if topic else "docs_all"
        return self.get("documents", key)
    
    def set_document_list(self, documents: list, topic: Optional[str] = None, ttl: int = 1800) -> bool:
        """Set document list in cache (30 minutes TTL)."""
        key = f"docs_{topic}" if topic else "docs_all"
        return self.set("documents", key, documents, ttl)
    
    def invalidate_documents(self):
        """Invalidate all document caches."""
        self.clear_prefix("documents")

# Global cache instance
cache = RedisCache()
cache_service = cache 