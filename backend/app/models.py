"""
SQLAlchemy ORM models for Closira backend
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from datetime import datetime
from app.database import Base


class HealthCheck(Base):
    """
    Placeholder model for health checks.
    This serves as a test model to verify database connection.
    """
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), default="healthy")
    timestamp = Column(DateTime, default=datetime.utcnow)
    version = Column(String(50), default="1.0.0")
