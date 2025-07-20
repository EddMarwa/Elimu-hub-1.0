import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from app.config import settings
from app.utils.logger import logger

class RateLimiter:
    def __init__(self):
        self.requests_per_minute = defaultdict(list)
        self.requests_per_hour = defaultdict(list)
    
    def _clean_old_requests(self, requests_list: list, window_seconds: int):
        """Remove requests older than the time window."""
        current_time = time.time()
        return [req_time for req_time in requests_list if current_time - req_time < window_seconds]
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    def is_rate_limited(self, request: Request) -> bool:
        """Check if the request should be rate limited."""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        self.requests_per_minute[client_ip] = self._clean_old_requests(
            self.requests_per_minute[client_ip], 60
        )
        self.requests_per_hour[client_ip] = self._clean_old_requests(
            self.requests_per_hour[client_ip], 3600
        )
        
        # Check minute limit
        if len(self.requests_per_minute[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded per minute for IP: {client_ip}")
            return True
        
        # Check hour limit
        if len(self.requests_per_hour[client_ip]) >= settings.RATE_LIMIT_PER_HOUR:
            logger.warning(f"Rate limit exceeded per hour for IP: {client_ip}")
            return True
        
        # Add current request
        self.requests_per_minute[client_ip].append(current_time)
        self.requests_per_hour[client_ip].append(current_time)
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Skip rate limiting for health checks and static files
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    if rate_limiter.is_rate_limited(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    return await call_next(request) 