"""Analyze prompts command."""
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

from src.domain.value_objects.similarity import SimilarityMetric
from src.application.commands.base import ICommand


@dataclass
class AnalyzePromptsCommand(ICommand):
    """Command to analyze two prompts for similarity and safety."""
    user_id: str
    prompt1_text: str
    prompt2_text: str
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    similarity_threshold: float = 0.7
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate command parameters."""
        if not self.user_id:
            return False, "User ID is required"
        if not self.prompt1_text or not self.prompt2_text:
            return False, "Both prompts are required"
        if not 0 <= self.similarity_threshold <= 1:
            return False, "Similarity threshold must be between 0 and 1"
        return True, None


@dataclass
class AnalyzePromptsResult:
    """Result of prompt analysis."""
    success: bool
    prompt1_id: str
    prompt2_id: str
    similarity_scores: Dict[str, float]
    is_similar: bool
    llm_response: Optional[str] = None
    agent_analysis: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    explanation: Optional[str] = None