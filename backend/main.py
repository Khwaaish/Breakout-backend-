"""
Closira Backend API - Main FastAPI Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.logger import logger
from app.schemas import HealthCheckResponse
from app import crud, schemas

# Create FastAPI application
app = FastAPI(
    title="Closira Backend API",
    description="Backend API for Closira - Weather Intelligence Platform",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Closira Backend API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown"""
    logger.info("Shutting down Closira Backend API...")


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API is running and database is accessible.
    
    Returns:
        HealthCheckResponse: Status of the API and database connection
    """
    try:
        # Try to access the database
        db.execute("SELECT 1")
        
        return HealthCheckResponse(
            status="healthy",
            message="API is running and database connection is active",
            timestamp=datetime.utcnow(),
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}",
            timestamp=datetime.utcnow(),
            version="1.0.0"
        )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Closira Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
