import logging
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Security, Request, Response
from fastapi.responses import RedirectResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.bookings import router as bookings_router
from app.api.requests import router as requests_router
from app.api.hotel import router as hotel_router
from app.di import get_container, get_rag_service
from app.services.document_service import DocumentService
from app.settings.config import settings
from app.logging import setup_structured_logging, CorrelationIdMiddleware, get_correlation_id
from app.middleware import setup_rate_limiting, limiter, RequestValidationMiddleware

# Configure structured logging
setup_structured_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOTEL_DOCUMENT = PROJECT_ROOT / "data" / "hotel.txt"

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)
ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections",
)
CHROMADB_DOCUMENTS = Gauge(
    "chromadb_documents",
    "Number of documents in ChromaDB",
)

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
) -> str:
    """Verify API key from header."""
    # Get current settings to check API keys
    from app.settings.config import get_settings
    settings = get_settings()
    api_keys = set(settings.api_keys) if settings.api_keys else set()

    if not api_keys:
        # No API keys configured - allow all (development mode)
        return "development"

    if api_key not in api_keys:
        logger.warning(
            "Invalid API key attempted",
            extra={"api_key_prefix": api_key[:8] if api_key else "none", "correlation_id": get_correlation_id()},
        )
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Hotel AI Assistant", extra={"version": settings.app_version, "correlation_id": get_correlation_id()})

    if not HOTEL_DOCUMENT.is_file():
        logger.error("Hotel document not found", extra={"path": str(HOTEL_DOCUMENT), "correlation_id": get_correlation_id()})
        raise FileNotFoundError(f"Hotel document not found: {HOTEL_DOCUMENT}")

    document_service = DocumentService()
    text = document_service.load_document(str(HOTEL_DOCUMENT))
    chunks = document_service.split_into_chunks(text)

    if not chunks:
        logger.error("Hotel document contains no chunks", extra={"correlation_id": get_correlation_id()})
        raise RuntimeError("The hotel document contains no chunks.")

    # Initialize container (database, etc.)
    container = get_container()
    await container.initialize()
    
    # Seed database with initial data (admin user, etc.)
    from app.db.seed import seed_database
    await seed_database(container.user_repository)
    
    # Use the same RAG service instance that the API depends on
    rag_service = get_rag_service()
    await rag_service.add_chunks(chunks)
    
    # Update ChromaDB metric
    CHROMADB_DOCUMENTS.set(rag_service.collection.count())

    logger.info(
        "Hotel document ingested",
        extra={"chunks": len(chunks), "chromadb_count": rag_service.collection.count(), "correlation_id": get_correlation_id()},
    )

    yield

    # Shutdown
    logger.info("Shutting down Hotel AI Assistant", extra={"correlation_id": get_correlation_id()})
    
    # Close container resources
    container = get_container()
    await container.close()


# Custom middleware for metrics
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect Prometheus metrics."""
    start_time = time.time()
    ACTIVE_CONNECTIONS.inc()
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(duration)
        
        return response
    except Exception as e:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=500,
        ).inc()
        raise
    finally:
        ACTIVE_CONNECTIONS.dec()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Add metrics middleware
app.middleware("http")(metrics_middleware)

# Correlation ID middleware (must be first to capture all requests)
app.add_middleware(CorrelationIdMiddleware)

# Request validation middleware
app.add_middleware(
    RequestValidationMiddleware,
    max_body_size=1024 * 1024,  # 1 MB
    allowed_content_types=["application/json"],
)

# Rate limiting
setup_rate_limiting(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, dependencies=[Depends(verify_api_key)])
app.include_router(auth_router)  # Public - login/register
app.include_router(bookings_router, dependencies=[Depends(verify_api_key)])
app.include_router(requests_router, dependencies=[Depends(verify_api_key)])
app.include_router(hotel_router)  # Public - rooms, services, info


@app.get("/")
def redirect_to_endpoint():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status."""
    from app.di import get_container
    from app.memory.factory import get_memory_store
    
    container = get_container()
    rag_service = container.rag_service
    memory_store = get_memory_store()
    db_manager = container.db_manager
    
    # Check ChromaDB
    chroma_status = "healthy"
    chroma_count = 0
    try:
        chroma_count = rag_service.collection.count()
    except Exception:
        chroma_status = "unhealthy"
    
    # Check memory store
    memory_status = "healthy"
    try:
        sessions = await memory_store.list_sessions(limit=1)
    except Exception:
        memory_status = "unhealthy"
    
    # Check database
    db_status = "healthy"
    try:
        db_status = "healthy" if await db_manager.health_check() else "unhealthy"
    except Exception:
        db_status = "unhealthy"
    
    overall_status = "healthy" if all(s == "healthy" for s in [chroma_status, memory_status, db_status]) else "degraded"
    
    return {
        "status": overall_status,
        "version": settings.app_version,
        "dependencies": {
            "chromadb": {"status": chroma_status, "documents": chroma_count},
            "memory_store": {"status": memory_status},
            "database": {"status": db_status},
        },
    }


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )