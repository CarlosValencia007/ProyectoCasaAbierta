"""
Smart Classroom AI - Main Application
FastAPI application entry point with middleware and routing
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import SmartClassroomException
from app.api import enrollment, attendance, emotions, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Prefix: {settings.API_PREFIX}")
    
    # Test database connection
    from app.db.supabase_client import SupabaseClient
    try:
        db_status = await SupabaseClient.test_connection()
        if db_status:
            logger.info("✓ Database connection established")
        else:
            logger.warning("⚠ Database connection failed")
    except Exception as e:
        logger.error(f"✗ Database connection error: {str(e)}")
    
    # Test DeepFace availability
    try:
        from deepface import DeepFace
        logger.info("✓ DeepFace library loaded successfully")
    except Exception as e:
        logger.error(f"✗ DeepFace initialization error: {str(e)}")
    
    logger.info("="*80)
    logger.info("🚀 Application startup complete")
    logger.info("="*80)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Cleanup complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered classroom assistant for attendance tracking and emotional analysis. "
        "Uses facial recognition (DeepFace + Facenet) and emotion detection to provide "
        "real-time insights into classroom engagement."
    ),
    version=settings.APP_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS.split(","),
    allow_headers=settings.CORS_HEADERS.split(",") if settings.CORS_HEADERS != "*" else ["*"],
)

# GZip Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    start_time = time.time()
    
    logger.info(f"→ {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(SmartClassroomException)
async def smart_classroom_exception_handler(request: Request, exc: SmartClassroomException):
    """Handle custom application exceptions"""
    logger.error(f"SmartClassroom Exception: {exc.code} - {exc.message}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.code,
            "timestamp": time.time()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Request validation failed",
            "errors": exc.errors(),
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": time.time()
        }
    )


# ============================================================================
# ROUTER REGISTRATION
# ============================================================================

# Health check routes (no prefix)
app.include_router(health.router)

# API routes (with prefix)
app.include_router(enrollment.router, prefix=settings.API_PREFIX)
app.include_router(attendance.router, prefix=settings.API_PREFIX)
app.include_router(emotions.router, prefix=settings.API_PREFIX)


# ============================================================================
# DEVELOPMENT SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
