from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from datetime import datetime
import sys
import re

from app.config import settings
from app.models.response import HealthResponse, ErrorResponse
from app.core.chroma_engine import chroma_engine
from app.core.cache_manager import cache_manager

# Import API routers
from app.api import documents, query, llm, context
from app.api import query_excel, llm_excel


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    str(settings.log_path / "app.log"),
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    # Startup
    logger.info("Starting Office LLM Add-in Backend...")
    logger.info(f"Version: 2.5.0")
    logger.info(f"Environment: {'Development' if settings.API_ENV == 'development' else 'Production'}")
    
    # Initialize services
    try:
        # Test Chroma connection
        stats = chroma_engine.get_collection_stats()
        logger.info(f"Chroma initialized: {stats['document_count']} documents")
        
        # Clear expired cache
        cleared = cache_manager.clear_expired()
        logger.info(f"Cache cleared: {cleared} expired entries")
        
        cache_stats = cache_manager.get_stats()
        logger.info(f"Cache stats: {cache_stats}")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Office LLM Add-in Backend...")


# Create FastAPI app
app = FastAPI(
    title="Office LLM Add-in API",
    description="AI-powered Office Add-in for Word and Excel",
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware to sanitize request body
@app.middleware("http")
async def sanitize_request_body(request: Request, call_next):
    """Middleware to clean control characters from request body"""
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            # Read the request body
            body = await request.body()

            if body:
                # Decode and clean the body
                body_str = body.decode('utf-8')

                # Remove invalid control characters but keep \n, \r, \t
                # This regex removes control chars except newline (0x0A), carriage return (0x0D), and tab (0x09)
                cleaned_body = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', body_str)

                # Create a new request with cleaned body
                async def receive():
                    return {"type": "http.request", "body": cleaned_body.encode('utf-8')}

                request._receive = receive

        except Exception as e:
            logger.warning(f"Failed to sanitize request body: {e}")

    response = await call_next(request)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc) if settings.API_ENV == "development" else "An error occurred"
        ).dict()
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Chroma
        chroma_stats = chroma_engine.get_collection_stats()
        chroma_status = "healthy"
    except Exception as e:
        logger.error(f"Chroma health check failed: {e}")
        chroma_status = "unhealthy"
    
    # Check Cache
    try:
        cache_stats = cache_manager.get_stats()
        cache_status = "healthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        cache_status = "unhealthy"
    
    return HealthResponse(
        status="healthy" if chroma_status == "healthy" and cache_status == "healthy" else "degraded",
        version="2.5.0",
        timestamp=datetime.now(),
        services={
            "chroma": chroma_status,
            "cache": cache_status
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Office LLM Add-in API",
        "version": "2.5.0",
        "status": "running",
        "docs": "/docs"
    }


# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(query.router, prefix="/api/query", tags=["Word Query"])
app.include_router(llm.router, prefix="/api/llm", tags=["Word LLM"])
app.include_router(context.router, prefix="/api/context", tags=["Context"])
app.include_router(query_excel.router, prefix="/api/excel", tags=["Excel"])
app.include_router(llm_excel.router, prefix="/api/excel/llm", tags=["Excel LLM"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_ENV == "development"
    )