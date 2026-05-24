"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime


class HealthCheckCRUD:
    """CRUD operations for HealthCheck model"""

    @staticmethod
    def create(db: Session, health_check: schemas.HealthCheckCreate) -> models.HealthCheck:
        """Create a new health check record"""
        db_health_check = models.HealthCheck(
            status=health_check.status,
            version=health_check.version,
            timestamp=datetime.utcnow()
        )
        db.add(db_health_check)
        db.commit()
        db.refresh(db_health_check)
        return db_health_check

    @staticmethod
    def get_latest(db: Session) -> models.HealthCheck:
        """Get the latest health check record"""
        return db.query(models.HealthCheck).order_by(
            models.HealthCheck.id.desc()
        ).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 10):
        """Get all health check records with pagination"""
        return db.query(models.HealthCheck).offset(skip).limit(limit).all()
