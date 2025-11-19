"""
Lexikon API - Sprint 1 MVP
FastAPI backend with in-memory database for development.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import onboarding, users, terms, auth
from db.postgres import Base, engine

# Create FastAPI app
app = FastAPI(
    title="Lexikon API",
    description="Generic Lexical Ontology Service",
    version="0.1.0",
)

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
    """Create database tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

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
