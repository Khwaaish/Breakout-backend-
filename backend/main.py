"""
Closira Backend API - Main FastAPI Application
"""
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.logger import logger
from app.schemas import (
    HealthCheckResponse,
)
from app.routes.enquiry import router as enquiry_router

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

# Include enquiry routes from router
app.include_router(enquiry_router)


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
    # Attempt a lightweight DB check
    from sqlalchemy import text
    try:
        db.execute(text("SELECT 1"))
        logger.info({
            "event": "HEALTH_CHECK",
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })
        return HealthCheckResponse(status="healthy", database="connected", timestamp=datetime.utcnow())
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        logger.info({
            "event": "HEALTH_CHECK",
            "status": "unhealthy",
            "database": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        })
        from fastapi import JSONResponse
        return JSONResponse(status_code=500, content={"status": "unhealthy", "database": "error", "timestamp": datetime.utcnow().isoformat()})





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
