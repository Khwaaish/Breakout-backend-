from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    CreateEnquiryRequest,
    EnquiryResponse,
    FollowupRequest,
    FollowupResponse,
    EnquiryHistoryResponse,
)
from app.crud import EnquiryCRUD, TimelineEventCRUD, FollowupCRUD
from app.workers.background_tasks import process_enquiry_background
from app.logger import logger
import json
from datetime import datetime

router = APIRouter()


@router.post(
    "/enquiry",
    response_model=EnquiryResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Enquiries"],
    summary="Create a new enquiry",
    description="Submit a new customer enquiry. The enquiry is validated and immediately queued for processing."
)
async def create_enquiry(
    request: CreateEnquiryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> EnquiryResponse:
    enquiry = EnquiryCRUD.create_enquiry(
        db=db,
        customer_name=request.customer_name,
        channel=request.channel.value,
        message=request.message,
    )

    # Timeline event
    TimelineEventCRUD.create_timeline_event(db, enquiry.id, "ENQUIRY_CREATED")

    # Structured log
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "ENQUIRY_CREATED",
        "enquiry_id": str(enquiry.id),
        "details": f"job_id={enquiry.job_id}, channel={request.channel.value}"
    }))

    # Schedule background processing
    background_tasks.add_task(process_enquiry_background, enquiry.id)

    return EnquiryResponse(job_id=str(enquiry.job_id), status=enquiry.status, message="Enquiry received and queued for processing")


@router.post(
    "/enquiry/{job_id}/followup",
    response_model=FollowupResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Enquiries"],
    summary="Create a followup for an enquiry",
    description="Schedule a followup for an existing enquiry using job_id."
)
async def create_followup(job_id: str, request: FollowupRequest, db: Session = Depends(get_db)) -> FollowupResponse:
    enquiry = EnquiryCRUD.get_enquiry_by_job_id(db, job_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    followup = FollowupCRUD.create_followup(db=db, enquiry_id=enquiry.id, delay_minutes=request.delay_minutes, template_message=request.template_message)

    TimelineEventCRUD.create_timeline_event(db, enquiry.id, "FOLLOWUP_CREATED")
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "FOLLOWUP_CREATED",
        "enquiry_id": str(enquiry.id),
        "details": f"followup_id={followup.id}, delay_minutes={followup.delay_minutes}"
    }))

    return FollowupResponse(status="scheduled", scheduled_time=followup.scheduled_time)


@router.get(
    "/enquiry/{job_id}/history",
    response_model=EnquiryHistoryResponse,
    tags=["Enquiries"],
    summary="Get enquiry history",
    description="Fetch enquiry status, followups and timeline events for a job_id."
)
async def get_enquiry_history(job_id: str, db: Session = Depends(get_db)) -> EnquiryHistoryResponse:
    enquiry = EnquiryCRUD.get_enquiry_by_job_id(db, job_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    followups = FollowupCRUD.get_enquiry_followups(db, enquiry.id)
    timeline = TimelineEventCRUD.get_enquiry_timeline(db, enquiry.id)

    followup_items = [{"delay_minutes": f.delay_minutes, "scheduled_time": f.scheduled_time} for f in followups]
    timeline_items = [{"event": t.event, "timestamp": t.timestamp} for t in timeline]

    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "HISTORY_FETCHED",
        "enquiry_id": str(enquiry.id),
        "details": f"followups={len(followup_items)}, timeline={len(timeline_items)}"
    }))

    return EnquiryHistoryResponse(
        job_id=str(enquiry.job_id),
        status=enquiry.status,
        matched_sop=enquiry.matched_sop,
        escalation_reason=enquiry.escalation_reason,
        followups=followup_items,
        timeline=timeline_items,
    )
