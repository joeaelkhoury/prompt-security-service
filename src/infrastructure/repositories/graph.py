"""Graph repository implementation."""
from typing import List, Dict
import networkx as nx

from src.domain.entities.graph import GraphNode, GraphEdge
from src.domain.entities.prompt import PromptStatus
from src.domain.repositories.interfaces import IGraphRepository


class NetworkXGraphRepository(IGraphRepository):
    """NetworkX-based implementation of graph repository."""
    
    def __init__(self):
        self._graph = nx.DiGraph()
    
    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self._graph.add_node(
            node.id,
            node_type=node.node_type,
            data=node.data,
            created_at=node.created_at
        )
    
    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        self._graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_type=edge.edge_type,
            weight=edge.weight,
            metadata=edge.metadata
        )
    
    def find_similar_prompts(self, prompt_id: str, threshold: float) -> List[str]:
        """Find prompts similar to given prompt."""
        similar = []
        if prompt_id in self._graph:
            for neighbor in self._graph.neighbors(prompt_id):
                edge_data = self._graph[prompt_id][neighbor]
                if (edge_data.get('edge_type') == 'similar_to' and 
                    edge_data.get('weight', 0) >= threshold):
                    similar.append(neighbor)
        return similar
    
    def get_user_patterns(self, user_id: str) -> List[Dict]:
        """Get patterns for a user."""
        patterns = []
        if user_id in self._graph:
            # Find all prompts submitted by user
            user_prompts = [
                n for n in self._graph.neighbors(user_id)
                if self._graph.nodes[n].get('node_type') == 'prompt'
            ]
            
            # Analyze patterns
            blocked_count = sum(
                1 for p in user_prompts
                if self._graph.nodes[p].get('data', {}).get('status') == PromptStatus.BLOCKED.value
            )
            
            if blocked_count > 3:
                patterns.append({
                    'type': 'excessive_blocked_prompts',
                    'severity': 'high',
                    'count': blocked_count
                })
        
        return patterns
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> nx.Graph:
        """Get subgraph around a node."""
        if node_id not in self._graph:
            return nx.Graph()
        
        # Get all nodes within specified depth
        nodes = set([node_id])
        for _ in range(depth):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self._graph.neighbors(node))
                new_nodes.update(self._graph.predecessors(node))
            nodes.update(new_nodes)
        
        return self._graph.subgraph(nodes)