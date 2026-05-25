"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from backend.app import models, schemas
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Optional


# ============================================================================
# Enquiry CRUD Operations
# ============================================================================

class EnquiryCRUD:
    """CRUD operations for Enquiry model"""

    @staticmethod
    def create_enquiry(
        db: Session,
        customer_name: str,
        channel: str,
        message: str
    ) -> models.Enquiry:
        """
        Create a new enquiry with auto-generated job_id.
        
        Args:
            db: Database session
            customer_name: Customer name
            channel: Communication channel (whatsapp, email, call)
            message: Customer message
            
        Returns:
            Created enquiry object
        """
        try:
            db_enquiry = models.Enquiry(
                job_id=str(uuid4()),
                customer_name=customer_name,
                channel=channel,
                message=message,
                status="queued"
            )
            db.add(db_enquiry)
            db.commit()
            db.refresh(db_enquiry)
            return db_enquiry
        except SQLAlchemyError as e:
            db.rollback()
            raise

    @staticmethod
    def get_enquiry_by_id(db: Session, enquiry_id: int) -> Optional[models.Enquiry]:
        """
        Get enquiry by database ID.
        
        Args:
            db: Database session
            enquiry_id: Enquiry database ID
            
        Returns:
            Enquiry object or None
        """
        return db.query(models.Enquiry).filter(
            models.Enquiry.id == enquiry_id
        ).first()

    @staticmethod
    def get_enquiry_by_job_id(db: Session, job_id: str) -> Optional[models.Enquiry]:
        """
        Get enquiry by job_id (UUID).
        
        Args:
            db: Database session
            job_id: Unique job identifier
            
        Returns:
            Enquiry object or None
        """
        return db.query(models.Enquiry).filter(
            models.Enquiry.job_id == job_id
        ).first()

    @staticmethod
    def update_enquiry_status(
        db: Session,
        enquiry_id: int,
        new_status: str
    ) -> Optional[models.Enquiry]:
        """
        Update enquiry status.
        
        Args:
            db: Database session
            enquiry_id: Enquiry database ID
            new_status: New status value
            
        Returns:
            Updated enquiry object or None
        """
        try:
            enquiry = EnquiryCRUD.get_enquiry_by_id(db, enquiry_id)
            if not enquiry:
                return None
            
            enquiry.status = new_status
            enquiry.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(enquiry)
            return enquiry
        except SQLAlchemyError as e:
            db.rollback()
            raise

    @staticmethod
    def update_sop_result(
        db: Session,
        enquiry_id: int,
        matched_sop: str,
        suggested_response: str
    ) -> Optional[models.Enquiry]:
        """
        Update SOP matching results.
        
        Args:
            db: Database session
            enquiry_id: Enquiry database ID
            matched_sop: Matched SOP identifier
            suggested_response: Suggested response text
            
        Returns:
            Updated enquiry object or None
        """
        try:
            enquiry = EnquiryCRUD.get_enquiry_by_id(db, enquiry_id)
            if not enquiry:
                return None
            
            enquiry.matched_sop = matched_sop
            enquiry.suggested_response = suggested_response
            enquiry.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(enquiry)
            return enquiry
        except SQLAlchemyError as e:
            db.rollback()
            raise

    @staticmethod
    def escalate_enquiry(
        db: Session,
        enquiry_id: int,
        reason: str
    ) -> Optional[models.Enquiry]:
        """
        Escalate an enquiry and record reason.
        
        Args:
            db: Database session
            enquiry_id: Enquiry database ID
            reason: Escalation reason
            
        Returns:
            Updated enquiry object or None
        """
        try:
            enquiry = EnquiryCRUD.get_enquiry_by_id(db, enquiry_id)
            if not enquiry:
                return None
            
            enquiry.status = "escalated"
            enquiry.escalation_reason = reason
            enquiry.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(enquiry)
            return enquiry
        except SQLAlchemyError as e:
            db.rollback()
            raise

    @staticmethod
    def get_enquiry_history(
        db: Session,
        enquiry_id: int
    ) -> Optional[models.Enquiry]:
        """
        Get enquiry with all related followups and timeline events.
        Uses eager loading for efficiency.
        
        Args:
            db: Database session
            enquiry_id: Enquiry database ID
            
        Returns:
            Enquiry object with relationships loaded, or None
        """
        return db.query(models.Enquiry).options(
            joinedload(models.Enquiry.followups),
            joinedload(models.Enquiry.timeline_events)
        ).filter(models.Enquiry.id == enquiry_id).first()


# ============================================================================
# Followup CRUD Operations
# ============================================================================

class FollowupCRUD:
    """CRUD operations for Followup model"""

    @staticmethod
    def create_followup(
        db: Session,
        enquiry_id: int,
        delay_minutes: int,
        template_message: str
    ) -> models.Followup:
        """
        Create a new followup message.
        
        Args:
            db: Database session
            enquiry_id: Parent enquiry ID
            delay_minutes: Delay before sending (in minutes)
            template_message: Followup message template
            
        Returns:
            Created followup object
        """
        try:
            scheduled_time = datetime.utcnow() + timedelta(minutes=delay_minutes)
            
            db_followup = models.Followup(
                enquiry_id=enquiry_id,
                delay_minutes=delay_minutes,
                template_message=template_message,
                scheduled_time=scheduled_time
            )
            db.add(db_followup)
            db.commit()
            db.refresh(db_followup)
            return db_followup
        except SQLAlchemyError as e:
            db.rollback()
            raise

    @staticmethod
    def get_followup(db: Session, followup_id: int) -> Optional[models.Followup]:
        """
        Get followup by ID.
        
        Args:
            db: Database session
            followup_id: Followup ID
            
        Returns:
            Followup object or None
        """
        return db.query(models.Followup).filter(
            models.Followup.id == followup_id
        ).first()

    @staticmethod
    def get_enquiry_followups(
        db: Session,
        enquiry_id: int
    ) -> list[models.Followup]:
        """
        Get all followups for an enquiry.
        
        Args:
            db: Database session
            enquiry_id: Parent enquiry ID
            
        Returns:
            List of followup objects
        """
        return db.query(models.Followup).filter(
            models.Followup.enquiry_id == enquiry_id
        ).order_by(models.Followup.scheduled_time).all()


# ============================================================================
# Timeline Event CRUD Operations
# ============================================================================

class TimelineEventCRUD:
    """CRUD operations for TimelineEvent model"""

    @staticmethod
    def create_timeline_event(
        db: Session,
        enquiry_id: int,
        event: str
    ) -> models.TimelineEvent:
        """
        Create a new timeline event for an enquiry.
        
        Args:
            db: Database session
            enquiry_id: Parent enquiry ID
            event: Event description
            
        Returns:
            Created timeline event object
        """
        try:
            db_event = models.TimelineEvent(
                enquiry_id=enquiry_id,
                event=event,
                timestamp=datetime.utcnow()
            )
            db.add(db_event)
            db.commit()
            db.refresh(db_event)
            return db_event
        except SQLAlchemyError as e:
            db.rollback()
            raise

    @staticmethod
    def get_enquiry_timeline(
        db: Session,
        enquiry_id: int
    ) -> list[models.TimelineEvent]:
        """
        Get all timeline events for an enquiry.
        
        Args:
            db: Database session
            enquiry_id: Parent enquiry ID
            
        Returns:
            List of timeline event objects
        """
        return db.query(models.TimelineEvent).filter(
            models.TimelineEvent.enquiry_id == enquiry_id
        ).order_by(models.TimelineEvent.timestamp).all()


# ============================================================================
# Legacy Health Check CRUD (Keep for backward compatibility if needed)
# ============================================================================
# Note: HealthCheck model was removed from ORM layer (API-only endpoint)
# Keeping this class structure for reference if health check DB storage
# is needed in the future

# class HealthCheckCRUD:
#     """CRUD operations for HealthCheck model"""
#
#     @staticmethod
#     def create(db: Session, health_check: schemas.HealthCheckCreate) -> models.HealthCheck:
#         """Create a new health check record"""
#         db_health_check = models.HealthCheck(
#             status=health_check.status,
#             version=health_check.version,
#             timestamp=datetime.utcnow()
#         )
#         db.add(db_health_check)
#         db.commit()
#         db.refresh(db_health_check)
#         return db_health_check
#
#     @staticmethod
#     def get_latest(db: Session) -> models.HealthCheck:
#         """Get the latest health check record"""
#         return db.query(models.HealthCheck).order_by(
#             models.HealthCheck.id.desc()
#         ).first()
#
#     @staticmethod
#     def get_all(db: Session, skip: int = 0, limit: int = 10):
#         """Get all health check records with pagination"""
#         return db.query(models.HealthCheck).offset(skip).limit(limit).all()
