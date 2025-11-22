"""
Lexikon API - Sprint 1 MVP
FastAPI backend with in-memory database for development.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from api import onboarding, users, terms, auth
from db.postgres import Base, engine
from middleware.rate_limit import limiter
from middleware.error_handler import setup_error_handlers
from config.secrets_validator import validate_secrets, SecretValidationError, is_production

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lexikon API",
    description="Generic Lexical Ontology Service",
    version="0.1.0",
)

# Setup error handlers (must be before route registration)
setup_error_handlers(app)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Load origins from environment variable
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    """Initialize application on startup"""
    # Validate secrets first (fail fast if configuration is wrong in production)
    try:
        validate_secrets(strict=is_production())
    except SecretValidationError as e:
        logger.error(f"Secret validation failed: {e}")
        raise

    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Application startup complete")

# Include routers
app.include_router(onboarding.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(terms.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Lexikon API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
