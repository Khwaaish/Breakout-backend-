"""
Closira Backend API - Main FastAPI Application
"""
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.logger import logger
from app.schemas import HealthCheckResponse, CreateEnquiryRequest, EnquiryResponse
from app.crud import EnquiryCRUD
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


@app.post(
    "/enquiry",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Enquiries"],
    summary="Create a new enquiry",
    description="Submit a new customer enquiry. The enquiry is validated and immediately queued for processing."
)
async def create_enquiry(
    request: CreateEnquiryRequest,
    db: Session = Depends(get_db)
) -> EnquiryResponse:
    """
    Create a new customer enquiry.
    
    - **customer_name**: Name of the customer (required, min 1 char)
    - **channel**: Communication channel - must be one of: whatsapp, email, call
    - **message**: Customer message (required, min 1 char)
    
    Returns:
        EnquiryResponse with job_id, status, and message
        
    Status Codes:
        - 201: Enquiry successfully created and queued
        - 422: Invalid request parameters
    """
    try:
        # Create enquiry in database
        enquiry = EnquiryCRUD.create_enquiry(
            db=db,
            customer_name=request.customer_name,
            channel=request.channel.value,  # Extract enum value
            message=request.message
        )
        
        logger.info(f"Enquiry created: job_id={enquiry.job_id}, channel={request.channel}")
        
        # Return response
        return EnquiryResponse(
            job_id=str(enquiry.job_id),
            status=enquiry.status,
            message="Enquiry received and queued for processing"
        )
    except Exception as e:
        logger.error(f"Error creating enquiry: {e}")
        raise


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
