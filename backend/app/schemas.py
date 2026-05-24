"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ChannelEnum(str, Enum):
    """Allowed communication channels"""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    CALL = "call"


# ============================================================================
# Request Schemas
# ============================================================================

class CreateEnquiryRequest(BaseModel):
    """Schema for creating a new enquiry"""
    customer_name: str = Field(
        ...,
        min_length=1,
        description="Customer name",
        examples=["John Doe"]
    )
    channel: ChannelEnum = Field(
        ...,
        description="Communication channel",
        examples=["email"]
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Customer message",
        examples=["Need pricing information"]
    )

    @field_validator("customer_name", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Strip leading and trailing whitespace"""
        if isinstance(v, str):
            return v.strip()
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "customer_name": "John Doe",
            "channel": "email",
            "message": "Need pricing information"
        }
    }}


class FollowupRequest(BaseModel):
    """Schema for creating a followup message"""
    delay_minutes: int = Field(
        ...,
        gt=0,
        description="Delay in minutes before sending followup",
        examples=[30]
    )
    template_message: str = Field(
        ...,
        min_length=1,
        description="Followup message template",
        examples=["Checking if you still need assistance"]
    )

    @field_validator("template_message", mode="before")
    @classmethod
    def strip_message_whitespace(cls, v):
        """Strip leading and trailing whitespace"""
        if isinstance(v, str):
            return v.strip()
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "delay_minutes": 30,
            "template_message": "Checking if you still need assistance"
        }
    }}


class EscalateRequest(BaseModel):
    """Schema for escalating an enquiry"""
    reason: str = Field(
        ...,
        min_length=1,
        description="Escalation reason",
        examples=["No SOP match found"]
    )

    @field_validator("reason", mode="before")
    @classmethod
    def strip_reason_whitespace(cls, v):
        """Strip leading and trailing whitespace"""
        if isinstance(v, str):
            return v.strip()
        return v

    model_config = {"json_schema_extra": {
        "example": {
            "reason": "No SOP match found"
        }
    }}


# ============================================================================
# Response Schemas
# ============================================================================

class EnquiryResponse(BaseModel):
    """Response schema for enquiry"""
    job_id: str = Field(
        ...,
        description="Unique job identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    status: str = Field(
        ...,
        description="Enquiry status",
        examples=["queued"]
    )
    message: str = Field(
        ...,
        description="Customer message",
        examples=["Need pricing information"]
    )

    class Config:
        from_attributes = True


class FollowupResponse(BaseModel):
    """Response schema for followup"""
    status: str = Field(
        ...,
        description="Followup status",
        examples=["scheduled"]
    )
    scheduled_time: datetime = Field(
        ...,
        description="Scheduled time for followup"
    )

    class Config:
        from_attributes = True


class EscalationResponse(BaseModel):
    """Response schema for escalation"""
    status: str = Field(
        ...,
        description="Escalation status",
        examples=["escalated"]
    )
    reason: str = Field(
        ...,
        description="Escalation reason",
        examples=["No SOP match found"]
    )

    class Config:
        from_attributes = True


# ============================================================================
# Legacy Health Check Schemas (Keep for backward compatibility)
# ============================================================================

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
