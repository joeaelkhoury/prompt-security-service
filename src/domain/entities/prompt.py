"""Prompt entity following DDD principles."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

from src.core.exceptions import DomainException


class PromptStatus(Enum):
    """Status of prompt processing."""
    PENDING = "pending"
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


@dataclass
class Prompt:
    """Domain entity representing a user prompt.
    
    This entity encapsulates the business logic for a prompt submission,
    including validation and safety scoring.
    """
    user_id: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sanitized_content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: PromptStatus = PromptStatus.PENDING
    safety_score: float = 0.0
    
    def __post_init__(self):
        """Validate prompt after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate prompt data."""
        if not self.content:
            raise DomainException("Prompt content cannot be empty")
        if len(self.content) > 5000:
            raise DomainException("Prompt content exceeds maximum length of 5000 characters")
        if not self.user_id:
            raise DomainException("User ID is required")
    
    def is_safe(self) -> bool:
        """Check if prompt is safe based on safety score."""
        return self.safety_score < 0.5
    
    def mark_as_blocked(self, reason: str) -> None:
        """Mark prompt as blocked with reason."""
        self.status = PromptStatus.BLOCKED
        self.safety_score = 1.0
    
    def update_safety_score(self, score: float) -> None:
        """Update safety score with validation."""
        if not 0 <= score <= 1:
            raise DomainException("Safety score must be between 0 and 1")
        self.safety_score = score