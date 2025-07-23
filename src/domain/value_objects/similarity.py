"""Similarity value objects."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.core.exceptions import DomainException


class SimilarityMetric(Enum):
    """Supported similarity metrics."""
    COSINE = "cosine"
    JACCARD = "jaccard"
    LEVENSHTEIN = "levenshtein"
    EMBEDDING = "embedding"


@dataclass
class SimilarityResult:
    """Value object for similarity comparison results."""
    prompt1_id: str
    prompt2_id: str
    metric: SimilarityMetric
    score: float
    timestamp: datetime = datetime.utcnow()
    
    def __post_init__(self):
        """Validate similarity result."""
        if not 0 <= self.score <= 1:
            raise DomainException("Similarity score must be between 0 and 1")
    
    def is_similar(self, threshold: float = 0.7) -> bool:
        """Check if prompts are similar based on threshold."""
        if not 0 <= threshold <= 1:
            raise DomainException("Threshold must be between 0 and 1")
        return self.score >= threshold