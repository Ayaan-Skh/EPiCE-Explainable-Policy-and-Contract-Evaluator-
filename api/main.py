import sys
sys.path.append("..")
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from src.logger import logging
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🚀 Startup
    logging.info("=" * 80)
    logging.info("🚀 Starting Insurance Q&A API")
    logging.info("=" * 80)
    logging.info("FastAPI server is starting...")
    logging.info("API Documentation: http://localhost:8000/docs")
    logging.info("Health Check: http://localhost:8000/api/health")
    logging.info("=" * 80)

    # If you ever need to init DB/clients, do it here
    # e.g. connect to DB, load models, etc.

    yield  # ⬅️ FastAPI serves requests between startup and shutdown

    # 📴 Shutdown
    logging.info("Shutting down Insurance Q&A API...")
    # Close DB connections / clients here if you add them later


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="Insurance Q&A API",
    description="AI-powered insurance claim analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["Insurance Q&A"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Insurance Q&A API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
