"""Repository interfaces following DDD principles."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import networkx as nx

from src.domain.entities.prompt import Prompt
from src.domain.entities.user import UserProfile
from src.domain.entities.graph import GraphNode, GraphEdge


class IPromptRepository(ABC):
    """Interface for prompt data access."""
    
    @abstractmethod
    def save(self, prompt: Prompt) -> None:
        """Save a prompt to storage."""
        pass
    
    @abstractmethod
    def find_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """Find a prompt by ID."""
        pass
    
    @abstractmethod
    def find_by_user(self, user_id: str, limit: int = 10) -> List[Prompt]:
        """Find prompts by user ID."""
        pass
    
    @abstractmethod
    def find_recent_by_user(self, user_id: str, hours: int = 24) -> List[Prompt]:
        """Find recent prompts by user."""
        pass


class IUserProfileRepository(ABC):
    """Interface for user profile data access."""
    
    @abstractmethod
    def save(self, profile: UserProfile) -> None:
        """Save a user profile."""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Find a user profile by ID."""
        pass
    
    @abstractmethod
    def create_if_not_exists(self, user_id: str) -> UserProfile:
        """Create profile if it doesn't exist."""
        pass


class IGraphRepository(ABC):
    """Interface for graph data access."""
    
    @abstractmethod
    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        pass
    
    @abstractmethod
    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        pass
    
    @abstractmethod
    def find_similar_prompts(self, prompt_id: str, threshold: float) -> List[str]:
        """Find prompts similar to given prompt."""
        pass
    
    @abstractmethod
    def get_user_patterns(self, user_id: str) -> List[Dict]:
        """Get patterns for a user."""
        pass
    
    @abstractmethod
    def get_subgraph(self, node_id: str, depth: int = 2) -> nx.Graph:
        """Get subgraph around a node."""
        pass
