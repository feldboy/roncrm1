"""FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ..config.settings import get_settings
from ..utils.logging import get_logger
from .middleware.auth import AuthMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.rate_limiting import RateLimitMiddleware
from .routes import (
    auth,
    plaintiffs,
    law_firms,
    cases,
    documents,
    communications,
    agents,
    reports,
    webhooks,
)

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI CRM API server")
    
    # Initialize agent registry and start core agents
    from ..agents.base.registry import AgentRegistry
    
    registry = AgentRegistry()
    
    # Start core agents
    await registry.start_core_agents()
    
    # Store registry in app state
    app.state.agent_registry = registry
    
    logger.info("AI CRM API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI CRM API server")
    
    # Stop all agents
    if hasattr(app.state, 'agent_registry'):
        await app.state.agent_registry.shutdown_all_agents()
    
    logger.info("AI CRM API server shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance.
    """
    # Create FastAPI app
    app = FastAPI(
        title="AI CRM Multi-Agent System",
        description="AI-powered CRM system for pre-settlement funding with multi-agent architecture",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled errors."""
        logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
            },
            exc_info=True,
        )
        
        if settings.ENVIRONMENT == "production":
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "type": type(exc).__name__,
                }
            )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT,
        }
    
    # Agent status endpoint
    @app.get("/agents/status")
    async def agents_status(request: Request):
        """Get status of all agents."""
        if hasattr(request.app.state, 'agent_registry'):
            registry = request.app.state.agent_registry
            return await registry.get_system_status()
        else:
            return {"error": "Agent registry not available"}
    
    # Include API routes
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(plaintiffs.router, prefix="/api/v1/plaintiffs", tags=["Plaintiffs"])
    app.include_router(law_firms.router, prefix="/api/v1/law-firms", tags=["Law Firms"])
    app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
    app.include_router(communications.router, prefix="/api/v1/communications", tags=["Communications"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
    app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
    
    return app


def run_server():
    """Run the development server."""
    uvicorn.run(
        "src.api.app:create_app",
        factory=True,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    run_server()