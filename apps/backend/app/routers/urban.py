from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.urban_orchestrator import urban_orchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/report", status_code=200)
async def report_urban_incident(
    report: Dict[str, str],
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Endpoint for reporting urban incidents.
    Triggers the 4-agent Smart City pipeline.
    """
    report_text = report.get("text")
    if not report_text:
        raise HTTPException(status_code=400, detail="Report text is required")

    logger.info(f"Received urban report from user {current_user.id}: {report_text[:50]}...")

    # Run the pipeline synchronously for immediate feedback in the hackathon demo
    pipeline_results = await urban_orchestrator.run_pipeline(report_text)

    return pipeline_results
