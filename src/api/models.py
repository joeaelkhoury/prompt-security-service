"""API request/response models."""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from datetime import datetime

from src.domain.value_objects.similarity import SimilarityMetric


class PromptAnalysisRequest(BaseModel):
    """Request model for prompt analysis."""
    user_id: str = Field(..., description="User identifier")
    prompt1: str = Field(..., description="First prompt text", min_length=1, max_length=5000)
    prompt2: str = Field(..., description="Second prompt text", min_length=1, max_length=5000)
    similarity_metric: SimilarityMetric = Field(
        default=SimilarityMetric.COSINE,
        description="Similarity metric to use"
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Threshold for considering prompts similar",
        ge=0.0,
        le=1.0
    )
    
    @validator('prompt1', 'prompt2')
    def validate_prompts(cls, v):
        """Validate prompt is not empty."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v



class PromptAnalysisResponse(BaseModel):
    """Response model for prompt analysis."""
    success: bool
    prompt1_id: str
    prompt2_id: str
    similarity_scores: Dict[str, float]
    is_similar: bool
    llm_response: Optional[str] = None
    explanation: str
    agent_findings: Optional[List[Dict]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str


class MetricsResponse(BaseModel):
    """Service metrics response."""
    total_requests: int
    total_users: int
    blocked_prompts: int
    average_similarity: float
    available_metrics: List[str]


class UserProfileResponse(BaseModel):
    """User profile response."""
    user_id: str
    reputation_score: float
    total_prompts: int
    blocked_prompts: int
    is_trusted: bool
    patterns: List[Dict]
    last_activity: str


class GraphVisualizationResponse(BaseModel):
    """Graph visualization response."""
    nodes: List[Dict]
    edges: List[Dict]
    center_node: str
