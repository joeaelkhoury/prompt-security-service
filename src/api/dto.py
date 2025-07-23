from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class PromptAnalysisRequestDTO(BaseModel):
    prompt1: str = Field(..., min_length=1, max_length=5000)
    prompt2: str = Field(..., min_length=1, max_length=5000)
    similarity_metric: str = Field(default="cosine")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    @validator('prompt1', 'prompt2')
    def validate_prompts(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v
    
    @root_validator
    def validate_metric(cls, values):
        valid_metrics = ["cosine", "jaccard", "levenshtein", "embedding"]
        if values.get('similarity_metric') not in valid_metrics:
            raise ValueError(f"Invalid metric. Must be one of {valid_metrics}")
        return values

class SecurityFindingDTO(BaseModel):
    agent: str
    recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)
    details: Optional[Dict[str, Any]] = None

class PromptAnalysisResponseDTO(BaseModel):
    success: bool
    prompt1_id: str
    prompt2_id: str
    similarity_scores: Dict[str, float]
    is_similar: bool
    llm_response: Optional[str] = None
    explanation: str
    agent_findings: List[SecurityFindingDTO]
    processing_time: float
    timestamp: datetime

class UserProfileDTO(BaseModel):
    user_id: str
    reputation_score: float = Field(ge=0.0, le=1.0)
    total_prompts: int = Field(ge=0)
    blocked_prompts: int = Field(ge=0)
    is_trusted: bool
    patterns: List[Dict[str, Any]]
    last_activity: datetime
    risk_level: str  # "low", "medium", "high"
    
    @root_validator
    def calculate_risk_level(cls, values):
        reputation = values.get('reputation_score', 1.0)
        if reputation > 0.8:
            values['risk_level'] = 'low'
        elif reputation > 0.5:
            values['risk_level'] = 'medium'
        else:
            values['risk_level'] = 'high'
        return values

class ErrorResponseDTO(BaseModel):
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None