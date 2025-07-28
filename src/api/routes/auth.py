"""Authentication API routes."""

from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr

from ...config.settings import get_settings
from ...utils.logging import get_logger
from ..middleware.auth import JWTManager

logger = get_logger(__name__)
settings = get_settings()
security = HTTPBearer()

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.
    
    Args:
        request: Login credentials.
        
    Returns:
        LoginResponse: JWT tokens and user information.
    """
    try:
        # In a real implementation, this would:
        # 1. Validate credentials against database
        # 2. Check password hash
        # 3. Retrieve user permissions and role
        
        # For demo purposes, using hardcoded credentials
        if request.email == "admin@example.com" and request.password == "admin123":
            user_data = {
                "user_id": "admin-user-id",
                "email": request.email,
                "name": "Admin User",
                "role": "admin",
                "permissions": [
                    "read:plaintiffs",
                    "write:plaintiffs",
                    "read:law_firms",
                    "write:law_firms",
                    "read:cases",
                    "write:cases",
                    "read:documents",
                    "write:documents",
                    "read:communications",
                    "write:communications",
                    "read:reports",
                    "admin:agents",
                ],
                "law_firm_id": "admin-law-firm",
            }
        elif request.email == "user@example.com" and request.password == "user123":
            user_data = {
                "user_id": "regular-user-id",
                "email": request.email,
                "name": "Regular User",
                "role": "user",
                "permissions": [
                    "read:plaintiffs",
                    "read:law_firms",
                    "read:cases",
                    "read:documents",
                    "read:communications",
                ],
                "law_firm_id": "user-law-firm",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        access_token = JWTManager.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            name=user_data["name"],
            role=user_data["role"],
            permissions=user_data["permissions"],
            law_firm_id=user_data["law_firm_id"],
        )
        
        refresh_token = JWTManager.create_refresh_token(
            user_id=user_data["user_id"]
        )
        
        logger.info(
            "User logged in successfully",
            user_id=user_data["user_id"],
            email=user_data["email"],
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request.
        
    Returns:
        RefreshTokenResponse: New access token.
    """
    try:
        # Refresh the access token
        new_access_token = JWTManager.refresh_access_token(request.refresh_token)
        
        if not new_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(request: Request):
    """
    Logout user (invalidate token).
    
    Note: In a production system, you would typically:
    1. Add the token to a blacklist
    2. Store blacklisted tokens in Redis with TTL
    3. Check blacklist in auth middleware
    """
    user_id = getattr(request.state, 'user_id', None)
    
    if user_id:
        logger.info(f"User logged out", user_id=user_id)
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Returns:
        Dict: Current user information.
    """
    user = getattr(request.state, 'user', None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "user": user,
        "authenticated": True,
    }


@router.get("/permissions")
async def get_user_permissions(request: Request) -> Dict[str, Any]:
    """
    Get current user's permissions.
    
    Returns:
        Dict: User permissions.
    """
    user = getattr(request.state, 'user', None)
    permissions = getattr(request.state, 'permissions', [])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return {
        "user_id": user["user_id"],
        "role": user["role"],
        "permissions": permissions,
    }