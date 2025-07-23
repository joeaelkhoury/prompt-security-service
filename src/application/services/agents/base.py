"""Base agent interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class ISecurityAgent(ABC):
    """Interface for security agents."""
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the given context and return findings."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get agent name."""
        pass
