"""
SQLAlchemy ORM models for Closira backend
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from app.database import Base


class Enquiry(Base):
    """
    Customer enquiry model
    """
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(UUID(as_uuid=False), unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    customer_name = Column(String(255), nullable=False)
    channel = Column(String(50), index=True, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), index=True, nullable=False, default="queued")
    matched_sop = Column(String(255), nullable=True)
    suggested_response = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    followups = relationship("Followup", back_populates="enquiry", cascade="all, delete-orphan", lazy="select")
    timeline_events = relationship("TimelineEvent", back_populates="enquiry", cascade="all, delete-orphan", lazy="select")


class Followup(Base):
    """
    Followup message for an enquiry
    """
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    enquiry_id = Column(Integer, ForeignKey("enquiries.id", ondelete="CASCADE"), nullable=False)
    delay_minutes = Column(Integer, nullable=False)
    template_message = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)

    # Relationships
    enquiry = relationship("Enquiry", back_populates="followups", lazy="select")


class TimelineEvent(Base):
    """
    Timeline event tracking for an enquiry
    """
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    enquiry_id = Column(Integer, ForeignKey("enquiries.id", ondelete="CASCADE"), nullable=False)
    event = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    enquiry = relationship("Enquiry", back_populates="timeline_events", lazy="select")
