"""
Background task worker functions for processing enquiries
"""
from app.database import SessionLocal
from app.services.sop_matcher import match_sop
from app.crud import EnquiryCRUD, TimelineEventCRUD
from app.logger import logger
from datetime import datetime
import json


def _log_event(event: str, enquiry_id: int, details: str | None = None):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "enquiry_id": str(enquiry_id),
        "details": details or ""
    }
    logger.info(json.dumps(payload))


def process_enquiry_background(enquiry_id: int) -> None:
    """
    Background worker to process a single enquiry.

    Steps:
    - Open a new DB session (do not reuse request session)
    - Fetch enquiry by id
    - Run SOP matching
    - If matched: update SOP fields, set status="processed", create timeline event
    - If not matched: escalate enquiry, set status="escalated", create timeline event
    - Log structured events
    - Ensure DB session closed and exceptions handled safely
    """
    db = SessionLocal()
    try:
        _log_event("PROCESSING_STARTED", enquiry_id, "Background worker started")

        enquiry = EnquiryCRUD.get_enquiry_by_id(db, enquiry_id)
        if not enquiry:
            _log_event("PROCESSING_ERROR", enquiry_id, "Enquiry not found")
            return

        # Run SOP matcher
        sop_result = match_sop(enquiry.message)

        if sop_result:
            # Update SOP fields and mark processed
            EnquiryCRUD.update_sop_result(
                db,
                enquiry_id,
                matched_sop=sop_result["sop"],
                suggested_response=sop_result["response"]
            )
            EnquiryCRUD.update_enquiry_status(db, enquiry_id, "processed")

            # Create timeline event
            TimelineEventCRUD.create_timeline_event(
                db,
                enquiry_id,
                f"SOP matched: {sop_result['sop']}"
            )

            _log_event("SOP_MATCHED", enquiry_id, json.dumps({"sop": sop_result["sop"]}))
        else:
            # Escalate
            EnquiryCRUD.escalate_enquiry(db, enquiry_id, reason="No SOP match found")

            TimelineEventCRUD.create_timeline_event(
                db,
                enquiry_id,
                "Escalated due to missing SOP"
            )

            _log_event("ESCALATION_TRIGGERED", enquiry_id, "No SOP match found")

        _log_event("PROCESSING_FINISHED", enquiry_id, "Background worker finished")
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        _log_event("PROCESSING_ERROR", enquiry_id, str(e))
    finally:
        db.close()
