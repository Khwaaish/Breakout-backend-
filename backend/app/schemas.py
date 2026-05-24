"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HealthCheckResponse(BaseModel):
    """Response schema for health check endpoint"""
    status: str
    message: str
    timestamp: datetime
    version: str

    class Config:
        from_attributes = True


class HealthCheckCreate(BaseModel):
    """Schema for creating health check records"""
    status: str
    version: str

    class Config:
        from_attributes = True
