"""Rate limiting middleware for FastAPI."""

import time
from typing import Dict, Tuple
from collections import defaultdict

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(self, app):
        """Initialize rate limiting middleware."""
        super().__init__(app)
        
        # In-memory storage for rate limiting (use Redis in production)
        self.request_counts: Dict[str, list] = defaultdict(list)
        
        # Rate limiting rules by endpoint pattern
        self.rate_limits = {
            # Authentication endpoints
            "/api/v1/auth/login": (5, 300),      # 5 requests per 5 minutes
            "/api/v1/auth/register": (3, 300),   # 3 requests per 5 minutes
            
            # API endpoints (general)
            "/api/v1/": (100, 60),               # 100 requests per minute
            
            # Webhook endpoints
            "/api/v1/webhooks/": (1000, 60),     # 1000 requests per minute
            
            # Default rate limit
            "default": (60, 60),                 # 60 requests per minute
        }
        
        # Endpoints to exclude from rate limiting
        self.exclude_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting middleware."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit_for_path(request.url.path)
        
        # Check rate limit
        if not self._check_rate_limit(client_id, rate_limit):
            # Rate limit exceeded
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "client_id": client_id,
                    "path": request.url.path,
                    "method": request.method,
                    "rate_limit": rate_limit,
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_limit[0]} requests per {rate_limit[1]} seconds",
                    "retry_after": rate_limit[1],
                }
            )
        
        # Continue processing request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining_requests = self._get_remaining_requests(client_id, rate_limit)
        reset_time = self._get_reset_time(client_id, rate_limit)
        
        response.headers["X-RateLimit-Limit"] = str(rate_limit[0])
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for client (for rate limiting)."""
        # If user is authenticated, use user ID
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Otherwise, use IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _get_rate_limit_for_path(self, path: str) -> Tuple[int, int]:
        """Get rate limit configuration for specific path."""
        # Check for exact matches first
        for pattern, limit in self.rate_limits.items():
            if pattern == "default":
                continue
            
            if path.startswith(pattern):
                return limit
        
        # Return default rate limit
        return self.rate_limits["default"]
    
    def _check_rate_limit(
        self,
        client_id: str,
        rate_limit: Tuple[int, int]
    ) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Unique client identifier.
            rate_limit: Tuple of (max_requests, time_window_seconds).
            
        Returns:
            bool: True if request is allowed, False if rate limit exceeded.
        """
        max_requests, time_window = rate_limit
        current_time = time.time()
        
        # Get request history for this client
        request_times = self.request_counts[client_id]
        
        # Remove old requests outside the time window
        cutoff_time = current_time - time_window
        request_times[:] = [t for t in request_times if t > cutoff_time]
        
        # Check if we're within the limit
        if len(request_times) >= max_requests:
            return False
        
        # Record this request
        request_times.append(current_time)
        
        return True
    
    def _get_remaining_requests(
        self,
        client_id: str,
        rate_limit: Tuple[int, int]
    ) -> int:
        """Get number of remaining requests for client."""
        max_requests, time_window = rate_limit
        current_time = time.time()
        
        # Get recent request count
        request_times = self.request_counts[client_id]
        cutoff_time = current_time - time_window
        recent_requests = len([t for t in request_times if t > cutoff_time])
        
        return max(0, max_requests - recent_requests)
    
    def _get_reset_time(
        self,
        client_id: str,
        rate_limit: Tuple[int, int]
    ) -> int:
        """Get timestamp when rate limit resets."""
        _, time_window = rate_limit
        current_time = time.time()
        
        # Get oldest request in current window
        request_times = self.request_counts[client_id]
        cutoff_time = current_time - time_window
        recent_requests = [t for t in request_times if t > cutoff_time]
        
        if recent_requests:
            # Reset time is when the oldest request expires
            return int(recent_requests[0] + time_window)
        else:
            # No recent requests, reset time is now
            return int(current_time)
    
    def cleanup_old_records(self, max_age_hours: int = 24):
        """Clean up old rate limiting records."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        # Clean up old records
        for client_id in list(self.request_counts.keys()):
            request_times = self.request_counts[client_id]
            request_times[:] = [t for t in request_times if t > cutoff_time]
            
            # Remove empty entries
            if not request_times:
                del self.request_counts[client_id]
        
        logger.info(f"Cleaned up old rate limiting records older than {max_age_hours} hours")