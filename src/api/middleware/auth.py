"""Authentication middleware for FastAPI."""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API endpoints."""
    
    def __init__(self, app):
        """Initialize auth middleware."""
        super().__init__(app)
        self.security = HTTPBearer(auto_error=False)
        
        # Endpoints that don't require authentication
        self.public_endpoints = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/webhooks/pipedrive",
            "/api/v1/webhooks/twilio",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through auth middleware."""
        # Skip auth for public endpoints
        if request.url.path in self.public_endpoints:
            return await call_next(request)
        
        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Extract and validate JWT token
            auth_result = await self._authenticate_request(request)
            
            if auth_result["success"]:
                # Add user info to request state
                request.state.user = auth_result["user"]
                request.state.user_id = auth_result["user"]["user_id"]
                request.state.permissions = auth_result["user"].get("permissions", [])
            else:
                # Return authentication error
                return self._auth_error_response(auth_result["error"])
        
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return self._auth_error_response("Authentication failed")
        
        response = await call_next(request)
        return response
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate request using JWT token."""
        try:
            # Get Authorization header
            auth_header = request.headers.get("Authorization")
            
            if not auth_header:
                return {
                    "success": False,
                    "error": "Missing Authorization header",
                }
            
            # Extract token from "Bearer <token>" format
            if not auth_header.startswith("Bearer "):
                return {
                    "success": False,
                    "error": "Invalid Authorization header format",
                }
            
            token = auth_header.split(" ")[1]
            
            # Validate and decode JWT token
            try:
                payload = jwt.decode(
                    token,
                    settings.security.secret_key,
                    algorithms=[settings.security.algorithm]
                )
                
                # Check token expiration
                if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                    return {
                        "success": False,
                        "error": "Token has expired",
                    }
                
                # Extract user information
                user_info = {
                    "user_id": payload.get("sub"),
                    "email": payload.get("email"),
                    "name": payload.get("name"),
                    "role": payload.get("role", "user"),
                    "permissions": payload.get("permissions", []),
                    "law_firm_id": payload.get("law_firm_id"),
                }
                
                return {
                    "success": True,
                    "user": user_info,
                }
                
            except jwt.ExpiredSignatureError:
                return {
                    "success": False,
                    "error": "Token has expired",
                }
            except jwt.InvalidTokenError as e:
                return {
                    "success": False,
                    "error": f"Invalid token: {str(e)}",
                }
        
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            return {
                "success": False,
                "error": "Authentication failed",
            }
    
    def _auth_error_response(self, error_message: str):
        """Return authentication error response."""
        from fastapi.responses import JSONResponse
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Authentication failed",
                "message": error_message,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


class JWTManager:
    """JWT token management utilities."""
    
    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        name: str,
        role: str = "user",
        permissions: list = None,
        law_firm_id: str = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=settings.security.access_token_expire_minutes
                )
            
            payload = {
                "sub": user_id,
                "email": email,
                "name": name,
                "role": role,
                "permissions": permissions or [],
                "law_firm_id": law_firm_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access",
            }
            
            token = jwt.encode(
                payload,
                settings.security.secret_key,
                algorithm=settings.security.algorithm
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create JWT refresh token."""
        try:
            expire = datetime.utcnow() + timedelta(
                days=settings.security.refresh_token_expire_days
            )
            
            payload = {
                "sub": user_id,
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh",
            }
            
            token = jwt.encode(
                payload,
                settings.security.secret_key,
                algorithm=settings.security.algorithm
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[settings.security.algorithm]
            )
            
            return {
                "valid": True,
                "payload": payload,
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "valid": False,
                "error": "Token has expired",
            }
        except jwt.InvalidTokenError as e:
            return {
                "valid": False,
                "error": f"Invalid token: {str(e)}",
            }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            result = JWTManager.verify_token(refresh_token)
            
            if not result["valid"]:
                return None
            
            payload = result["payload"]
            
            # Check if it's actually a refresh token
            if payload.get("type") != "refresh":
                return None
            
            user_id = payload["sub"]
            
            # Here you would typically fetch user details from database
            # For now, creating a basic token
            new_token = JWTManager.create_access_token(
                user_id=user_id,
                email="",  # Would be fetched from DB
                name="",   # Would be fetched from DB
                role="user"
            )
            
            return new_token
            
        except Exception as e:
            logger.error(f"Failed to refresh access token: {e}")
            return None


def require_permissions(*required_permissions: str):
    """Decorator to require specific permissions for endpoint access."""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Check if user has required permissions
            user_permissions = getattr(request.state, 'permissions', [])
            
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_role(required_role: str):
    """Decorator to require specific role for endpoint access."""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Check if user has required role
            user = getattr(request.state, 'user', {})
            user_role = user.get('role', 'user')
            
            # Define role hierarchy
            role_hierarchy = {
                'admin': 3,
                'manager': 2,
                'user': 1,
            }
            
            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 999):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role privileges"
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator