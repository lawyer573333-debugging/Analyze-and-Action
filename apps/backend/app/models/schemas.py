from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid

class Evidence(BaseModel):
    citation: str = Field(description="Exact string quoted from the source text")
    page_number: Optional[int] = Field(None, description="Page number if available")

class InsightResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    insight: str = Field(description="A non-trivial, specific operational insight")
    category: str = Field(description="Category such as Risk, Opportunity, Inefficiency")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    evidence: List[Evidence] = Field(description="List of exact citations supporting this insight")

class QuantifiedImpact(BaseModel):
    metric: str = Field(description="e.g., 'hours', 'dollars', 'incidents'")
    projected_value: float = Field(description="The quantified number")

class ImpactResult(BaseModel):
    insight_id: str
    impact_score: int = Field(description="Impact on a scale of 0-100")
    urgency_score: int = Field(description="Urgency on a scale of 0-100")
    quantified_impact: Optional[QuantifiedImpact] = None

class ActionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rank: int = Field(description="Rank of action (1 is highest priority)")
    title: str = Field(description="Short actionable title")
    description: str = Field(description="Detailed explanation of what to do")
    parameters: Dict[str, Any] = Field(description="Key-value pairs required for simulated execution, e.g., {'webhook_url': '...', 'delay_ms': 500}")

class SimulationResult(BaseModel):
    action_id: str
    status: str = Field(description="e.g., 'success', 'failed'")
    before_state: Dict[str, Any] = Field(description="JSON representing the system state before the action")
    after_state: Dict[str, Any] = Field(description="JSON representing the system state after the action")
    execution_logs: List[str] = Field(description="Step-by-step logs of what was 'executed'")
