from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, Dict
from datetime import datetime, timezone
import time

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.pipeline import Pipeline, Insight, ImpactAnalysis, Action, PipelineStatusEnum
from app.routers.auth import get_current_user
from app.services.orchestration_service import orchestrator
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


async def process_document_task(pipeline_id: str, document_id: str, db: AsyncSession):
    """Background task to run the orchestration pipeline and save results."""
    try:
        # Mark pipeline as processing
        result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
        pipeline = result.scalars().first()
        
        if not pipeline:
            logger.error(f"Pipeline {pipeline_id} not found")
            return
        
        pipeline.status = PipelineStatusEnum.PROCESSING
        pipeline.started_at = datetime.now(timezone.utc)
        await db.commit()
        
        # Retrieve the document
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalars().first()
        
        if not document:
            logger.error(f"Document {document_id} not found for processing")
            pipeline.status = PipelineStatusEnum.FAILED
            pipeline.error_message = "Document not found"
            pipeline.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return
        
        start_time = time.time()
        
        try:
            # Run the pipeline
            pipeline_results = await orchestrator.run_pipeline(document)
            
            # Save results to database
            if pipeline_results:
                # Save insights
                for insight_data in pipeline_results.get("insights", []):
                    insight = Insight(
                        pipeline_id=pipeline_id,
                        headline=insight_data.get("headline", ""),
                        description=insight_data.get("description"),
                        evidence=insight_data.get("evidence"),
                        insight_type=insight_data.get("type"),
                        confidence_score=insight_data.get("confidence", 0.0)
                    )
                    db.add(insight)
                    await db.flush()
                    
                    # Save impact analysis
                    impact_data = insight_data.get("impact", {})
                    if impact_data:
                        impact = ImpactAnalysis(
                            pipeline_id=pipeline_id,
                            insight_id=insight.id,
                            impact_summary=impact_data.get("summary", ""),
                            urgency_score=impact_data.get("urgency_score", 0),
                            probability_score=impact_data.get("probability_score", 0),
                            magnitude_score=impact_data.get("magnitude_score", 0),
                            immediate_impacts=impact_data.get("immediate_impacts"),
                            long_term_impacts=impact_data.get("long_term_impacts"),
                            affected_areas=impact_data.get("affected_areas")
                        )
                        db.add(impact)
                        await db.flush()
                        
                        # Save actions
                        for idx, action_data in enumerate(impact_data.get("actions", [])):
                            action = Action(
                                pipeline_id=pipeline_id,
                                impact_id=impact.id,
                                title=action_data.get("title", ""),
                                description=action_data.get("description"),
                                priority_rank=idx,
                                action_category=action_data.get("category"),
                                estimated_effort=action_data.get("effort"),
                                expected_outcome=action_data.get("outcome"),
                                success_metrics=action_data.get("metrics"),
                                parameters=action_data.get("parameters")
                            )
                            db.add(action)
            
            # Mark pipeline as completed
            pipeline.status = PipelineStatusEnum.COMPLETED
            pipeline.result_data = pipeline_results
            pipeline.completed_at = datetime.now(timezone.utc)
            pipeline.duration_seconds = time.time() - start_time
            
            await db.commit()
            logger.info(f"Successfully processed document {document_id} in pipeline {pipeline_id}")
            
        except Exception as e:
            logger.error(f"Pipeline failed for document {document_id}: {str(e)}", exc_info=True)
            pipeline.status = PipelineStatusEnum.FAILED
            pipeline.error_message = str(e)
            pipeline.completed_at = datetime.now(timezone.utc)
            pipeline.duration_seconds = time.time() - start_time
            await db.commit()
            
    except Exception as e:
        logger.error(f"Unexpected error in process_document_task: {str(e)}", exc_info=True)

@router.post("/{document_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Submit a document for AI analysis via the 5-agent pipeline."""
    
    # Verify document belongs to user
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create a Pipeline record to track analysis
    pipeline = Pipeline(
        document_id=document_id,
        user_id=current_user.id,
        status=PipelineStatusEnum.PENDING
    )
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
    
    # Queue the pipeline execution in the background
    background_tasks.add_task(process_document_task, pipeline.id, document_id, db)
    
    return {
        "pipeline_id": pipeline.id,
        "message": "Analysis started",
        "document_id": document_id,
        "status": "pending",
        "polling_url": f"/api/v1/insights/{pipeline.id}/status"
    }


@router.get("/{pipeline_id}/status")
async def get_pipeline_status(
    pipeline_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Check the status of a running analysis pipeline."""
    
    result = await db.execute(
        select(Pipeline).where(
            Pipeline.id == pipeline_id,
            Pipeline.user_id == current_user.id
        )
    )
    pipeline = result.scalars().first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    response = {
        "pipeline_id": pipeline.id,
        "status": pipeline.status.value,
        "document_id": pipeline.document_id,
        "created_at": pipeline.created_at,
        "started_at": pipeline.started_at,
        "completed_at": pipeline.completed_at,
        "duration_seconds": pipeline.duration_seconds,
    }
    
    # Include results if completed
    if pipeline.status == PipelineStatusEnum.COMPLETED:
        response["result"] = pipeline.result_data
    
    # Include error if failed
    if pipeline.status == PipelineStatusEnum.FAILED:
        response["error"] = pipeline.error_message
    
    return response


@router.get("/{pipeline_id}/results")
async def get_pipeline_results(
    pipeline_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get the detailed results of a completed analysis pipeline."""
    
    result = await db.execute(
        select(Pipeline).where(
            Pipeline.id == pipeline_id,
            Pipeline.user_id == current_user.id
        )
    )
    pipeline = result.scalars().first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    if pipeline.status != PipelineStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline is still {pipeline.status.value}, cannot retrieve results yet"
        )
    
    # Fetch all related insights, impacts, and actions
    insights_result = await db.execute(
        select(Insight).where(Insight.pipeline_id == pipeline_id)
    )
    insights = insights_result.scalars().all()
    
    response = {
        "pipeline_id": pipeline.id,
        "document_id": pipeline.document_id,
        "status": pipeline.status.value,
        "completed_at": pipeline.completed_at,
        "duration_seconds": pipeline.duration_seconds,
        "insights": []
    }
    
    for insight in insights:
        insight_data = {
            "id": insight.id,
            "headline": insight.headline,
            "description": insight.description,
            "type": insight.insight_type,
            "confidence": insight.confidence_score,
            "evidence": insight.evidence
        }
        
        # Get related impact analysis
        impact_result = await db.execute(
            select(ImpactAnalysis).where(ImpactAnalysis.insight_id == insight.id)
        )
        impact = impact_result.scalars().first()
        
        if impact:
            actions_result = await db.execute(
                select(Action).where(Action.impact_id == impact.id)
            )
            actions = actions_result.scalars().all()
            
            insight_data["impact"] = {
                "id": impact.id,
                "summary": impact.impact_summary,
                "urgency_score": impact.urgency_score,
                "probability_score": impact.probability_score,
                "magnitude_score": impact.magnitude_score,
                "immediate_impacts": impact.immediate_impacts,
                "long_term_impacts": impact.long_term_impacts,
                "affected_areas": impact.affected_areas,
                "actions": [
                    {
                        "id": action.id,
                        "title": action.title,
                        "description": action.description,
                        "priority": action.priority_rank,
                        "category": action.action_category,
                        "effort": action.estimated_effort,
                        "outcome": action.expected_outcome,
                        "metrics": action.success_metrics,
                        "parameters": action.parameters
                    }
                    for action in actions
                ]
            }
        
        response["insights"].append(insight_data)
    
    return response
