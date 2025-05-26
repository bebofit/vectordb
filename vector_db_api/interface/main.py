"""
FastAPI application factory and main entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vector_db_api.interface.api.health import router as health_router
from vector_db_api.interface.api.chunks import router as chunks_router
from vector_db_api.interface.api.libraries import router as libraries_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="StakeAI Vector Database API",
        description="A high-performance vector database API with multiple search algorithms",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(libraries_router, prefix="/api/v1", tags=["libraries"])
    app.include_router(chunks_router, prefix="/api/v1", tags=["chunks"])

    return app


# Create the app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to StakeAI Vector Database API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    } 
