"""User entity following DDD principles."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from src.core.exceptions import DomainException


@dataclass
class UserProfile:
    """Domain entity representing a user's security profile."""
    user_id: str
    reputation_score: float = 1.0
    total_prompts: int = 0
    blocked_prompts: int = 0
    suspicious_patterns: List[str] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate user profile after initialization."""
        if not self.user_id:
            raise DomainException("User ID cannot be empty")
        if not 0 <= self.reputation_score <= 1:
            raise DomainException("Reputation score must be between 0 and 1")
    
    def update_reputation(self, is_safe: bool) -> None:
        """Update user reputation based on prompt safety."""
        if is_safe:
            self.reputation_score = min(1.0, self.reputation_score + 0.01)
        else:
            self.reputation_score = max(0.0, self.reputation_score - 0.1)
            self.blocked_prompts += 1
        
        self.total_prompts += 1
        self.last_activity = datetime.utcnow()
    
    def is_trusted(self) -> bool:
        """Check if user is trusted based on reputation."""
        return self.reputation_score > 0.5
    
    def add_suspicious_pattern(self, pattern: str) -> None:
        """Add a suspicious pattern to user's history."""
        if pattern not in self.suspicious_patterns:
            self.suspicious_patterns.append(pattern)