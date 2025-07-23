"""Graph entities for security analysis."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

from src.core.exceptions import DomainException


@dataclass
class GraphNode:
    """Node in the security graph."""
    id: str
    node_type: str  # 'user', 'prompt', 'pattern'
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate node data."""
        if not self.id:
            raise DomainException("Node ID cannot be empty")
        if self.node_type not in ['user', 'prompt', 'pattern']:
            raise DomainException(f"Invalid node type: {self.node_type}")


@dataclass
class GraphEdge:
    """Edge in the security graph."""
    source_id: str
    target_id: str
    edge_type: str  # 'submitted', 'similar_to', 'matches_pattern'
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate edge data."""
        if not self.source_id or not self.target_id:
            raise DomainException("Edge source and target IDs cannot be empty")
        if self.edge_type not in ['submitted', 'similar_to', 'matches_pattern']:
            raise DomainException(f"Invalid edge type: {self.edge_type}")
        if not 0 <= self.weight <= 1:
            raise DomainException("Edge weight must be between 0 and 1")