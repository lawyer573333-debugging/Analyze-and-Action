from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, Dict

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.routers.auth import get_current_user
from app.services.orchestration_service import orchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_document_task(document_id: str, db: AsyncSession):
    """Background task to run the orchestration pipeline and save results."""
    # Retrieve the document
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalars().first()
    
    if not document:
        logger.error(f"Document {document_id} not found for processing.")
        return
        
    try:
        # Run the pipeline
        pipeline_results = await orchestrator.run_pipeline(document)
        # TODO: Save results to PostgreSQL tables (insights, impact_analyses, actions)
        logger.info(f"Successfully processed document {document_id}")
    except Exception as e:
        logger.error(f"Pipeline failed for document {document_id}: {str(e)}")
        # TODO: Update pipeline status to 'failed' in DB

@router.post("/{document_id}/analyze", status_code=202)
async def analyze_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Submit a document for AI analysis via the 5-agent pipeline."""
    
    # Verify document belongs to user
    result = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Queue the pipeline execution in the background
    # In production, we'd create a Pipeline record in DB here with status="pending"
    background_tasks.add_task(process_document_task, document_id, db)
    
    return {"message": "Analysis started", "document_id": document_id, "status": "processing"}
