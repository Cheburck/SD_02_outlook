"""
Rate Limiting module for Email System.
Uses slowapi for rate limiting with Redis backend.
"""
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting.
    Uses X-Forwarded-For header if available, otherwise remote address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=[os.environ.get('RATE_LIMIT_DEFAULT', '100/minute')],
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    strategy=os.environ.get('RATE_LIMIT_STRATEGY', 'fixed-window')
)


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add rate limit headers if available
        if hasattr(request.state, '_rate_limit_limit'):
            response.headers["X-RateLimit-Limit"] = str(request.state._rate_limit_limit)
        if hasattr(request.state, '_rate_limit_remaining'):
            response.headers["X-RateLimit-Remaining"] = str(request.state._rate_limit_remaining)
        if hasattr(request.state, '_rate_limit_reset'):
            response.headers["X-RateLimit-Reset"] = str(request.state._rate_limit_reset)
        
        return response


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    Returns 429 Too Many Requests with proper headers.
    """
    retry_after = getattr(exc, 'retry_after', 60)
    
    return Response(
        content='{"detail": "Too Many Requests", "retry_after": ' + str(retry_after) + '}',
        status_code=429,
        media_type="application/json",
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(getattr(exc, 'limit', 0)),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + retry_after),
        }
    )


# Rate limit presets for different endpoint types
RATE_LIMITS = {
    # Authentication endpoints (strict limits)
    'auth_login': '10/minute',      # Token Bucket - защита от брутфорса
    'auth_register': '5/minute',    # Fixed Window - защита от спама
    
    # User endpoints
    'user_create': '10/minute',
    'user_search': '30/minute',     # Sliding Window - защита от злоупотребления поиском
    
    # Folder endpoints
    'folder_create': '20/minute',
    
    # Message endpoints
    'message_create': '30/minute',
    
    # General limits
    'read': '100/minute',           # GET запросы
    'write': '50/minute',           # POST запросы
}
