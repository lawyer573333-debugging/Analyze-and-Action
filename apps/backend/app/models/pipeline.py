"""Pipeline-related database models for analysis tracking and results storage."""

from typing import Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum

from app.models.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PipelineStatusEnum(str, enum.Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Pipeline(Base):
    """Represents an analysis pipeline execution."""
    
    __tablename__ = "pipelines"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(PipelineStatusEnum), default=PipelineStatusEnum.PENDING)
    error_message = Column(String, nullable=True)
    
    # Pipeline execution metadata
    input_data = Column(JSON, nullable=True)  # Store request data
    result_data = Column(JSON, nullable=True)  # Store final pipeline output
    
    # Relationships
    insights = relationship("Insight", back_populates="pipeline", cascade="all, delete-orphan")
    impact_analyses = relationship("ImpactAnalysis", back_populates="pipeline", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="pipeline", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Execution time tracking
    duration_seconds = Column(Float, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Pipeline {self.id} - {self.status}>"


class Insight(Base):
    """Represents an extracted insight from document analysis."""
    
    __tablename__ = "insights"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    pipeline_id = Column(String, ForeignKey("pipelines.id"), nullable=False)
    
    headline = Column(String, nullable=False)
    description = Column(String, nullable=True)
    evidence = Column(JSON, nullable=True)  # Supporting data
    
    insight_type = Column(String, nullable=True)  # e.g., "market_trend", "risk", "opportunity"
    confidence_score = Column(Float, default=0.0)  # 0-1 confidence level
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="insights")
    impact_analysis = relationship("ImpactAnalysis", back_populates="insight", uselist=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Insight {self.id} - {self.headline[:50]}>"


class ImpactAnalysis(Base):
    """Represents the impact analysis for an insight."""
    
    __tablename__ = "impact_analyses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    insight_id = Column(String, ForeignKey("insights.id"), nullable=False)
    pipeline_id = Column(String, ForeignKey("pipelines.id"), nullable=False)
    
    impact_summary = Column(String, nullable=False)
    
    # Impact scoring
    urgency_score = Column(Integer, default=0)  # 1-10 scale
    probability_score = Column(Integer, default=0)  # 1-10 scale
    magnitude_score = Column(Integer, default=0)  # 1-10 scale
    
    # Detailed impact breakdown
    immediate_impacts = Column(JSON, nullable=True)  # List of immediate effects
    long_term_impacts = Column(JSON, nullable=True)  # List of long-term effects
    affected_areas = Column(JSON, nullable=True)  # List of affected domains/departments
    
    # Relationships
    insight = relationship("Insight", back_populates="impact_analysis")
    pipeline = relationship("Pipeline", back_populates="impact_analyses")
    actions = relationship("Action", back_populates="impact_analysis", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    def __repr__(self) -> str:
        return f"<ImpactAnalysis {self.id}>"


class Action(Base):
    """Represents an actionable recommendation."""
    
    __tablename__ = "actions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    impact_id = Column(String, ForeignKey("impact_analyses.id"), nullable=False)
    pipeline_id = Column(String, ForeignKey("pipelines.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Action priority and classification
    priority_rank = Column(Integer, default=0)  # Sort order
    action_category = Column(String, nullable=True)  # e.g., "strategic", "tactical", "defensive"
    
    # Execution details
    estimated_effort = Column(String, nullable=True)  # "low", "medium", "high"
    expected_outcome = Column(String, nullable=True)
    success_metrics = Column(JSON, nullable=True)  # List of measurable outcomes
    
    # Action parameters
    parameters = Column(JSON, nullable=True)  # Flexible action-specific data
    
    # Relationships
    impact_analysis = relationship("ImpactAnalysis", back_populates="actions")
    pipeline = relationship("Pipeline", back_populates="actions")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Action {self.id} - {self.title[:50]}>"
