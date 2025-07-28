"""Logging middleware for FastAPI."""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ...utils.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app):
        """Initialize logging middleware."""
        super().__init__(app)
        
        # Endpoints to exclude from logging (to reduce noise)
        self.exclude_paths = {
            "/health",
            "/metrics",
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through logging middleware."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Log request
        start_time = time.time()
        
        # Extract client IP
        client_ip = self._get_client_ip(request)
        
        # Extract user info if available
        user_id = getattr(request.state, 'user_id', None)
        
        logger.info(
            "HTTP Request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("User-Agent"),
                "user_id": user_id,
                "headers": dict(request.headers),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "HTTP Response",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                    "user_id": user_id,
                }
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            # Calculate processing time for errors
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                "HTTP Request Error",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time": round(process_time, 4),
                    "user_id": user_id,
                },
                exc_info=True
            )
            
            # Re-raise the exception
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP from the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if request.client:
            return request.client.host
        
        return "unknown"