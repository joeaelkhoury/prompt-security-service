import json
import networkx as nx
from typing import List, Dict
from datetime import datetime

from src.domain.entities.graph import GraphNode, GraphEdge
from src.domain.repositories.interfaces import IGraphRepository

class RedisGraphRepository(IGraphRepository):
    """Redis-based graph repository for performance."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.graph_key = "security_graph"
        self.node_prefix = "node:"
        self.edge_prefix = "edge:"
        
    def add_node(self, node: GraphNode) -> None:
        """Add node to Redis."""
        node_key = f"{self.node_prefix}{node.id}"
        node_data = {
            'id': node.id,
            'node_type': node.node_type,
            'data': json.dumps(node.data),
            'created_at': node.created_at.isoformat()
        }
        
        # Store node
        self.redis.hset(node_key, mapping=node_data)
        
        # Add to node type set
        self.redis.sadd(f"nodes:{node.node_type}", node.id)
        
        # Set expiry for temporary nodes
        if node.node_type == 'prompt':
            self.redis.expire(node_key, 86400 * 7)  # 7 days
    
    def add_edge(self, edge: GraphEdge) -> None:
        """Add edge to Redis."""
        edge_key = f"{self.edge_prefix}{edge.source_id}:{edge.target_id}"
        edge_data = {
            'source_id': edge.source_id,
            'target_id': edge.target_id,
            'edge_type': edge.edge_type,
            'weight': edge.weight,
            'metadata': json.dumps(edge.metadata)
        }
        
        # Store edge
        self.redis.hset(edge_key, mapping=edge_data)
        
        # Add to adjacency lists
        self.redis.sadd(f"edges:out:{edge.source_id}", edge.target_id)
        self.redis.sadd(f"edges:in:{edge.target_id}", edge.source_id)
        
        # Add to edge type set
        self.redis.sadd(f"edges:{edge.edge_type}", edge_key)
    
    def find_similar_prompts(self, prompt_id: str, threshold: float) -> List[str]:
        """Find similar prompts using Redis."""
        similar = []
        
        # Get all outgoing edges
        neighbors = self.redis.smembers(f"edges:out:{prompt_id}")
        
        for neighbor in neighbors:
            edge_key = f"{self.edge_prefix}{prompt_id}:{neighbor}"
            edge_data = self.redis.hgetall(edge_key)
            
            if edge_data.get('edge_type') == 'similar_to':
                weight = float(edge_data.get('weight', 0))
                if weight >= threshold:
                    similar.append(neighbor)
        
        return similar
    
    def get_user_patterns(self, user_id: str) -> List[Dict]:
        """Get user patterns from Redis."""
        patterns = []
        
        # Get user's prompts
        prompts = self.redis.smembers(f"edges:out:{user_id}")
        blocked_count = 0
        
        for prompt_id in prompts:
            node_key = f"{self.node_prefix}{prompt_id}"
            node_data = self.redis.hgetall(node_key)
            
            if node_data:
                data = json.loads(node_data.get('data', '{}'))
                if data.get('status') == 'blocked':
                    blocked_count += 1
        
        if blocked_count > 3:
            patterns.append({
                'type': 'excessive_blocked_prompts',
                'severity': 'high',
                'count': blocked_count
            })
        
        return patterns
    
    def get_subgraph(self, node_id: str, depth: int = 2) -> nx.Graph:
        """Build subgraph from Redis data."""
        G = nx.DiGraph()
        visited = set()
        to_visit = [(node_id, 0)]
        
        while to_visit:
            current_id, current_depth = to_visit.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            
            # Add node
            node_data = self.redis.hgetall(f"{self.node_prefix}{current_id}")
            if node_data:
                G.add_node(
                    current_id,
                    node_type=node_data.get('node_type'),
                    data=json.loads(node_data.get('data', '{}')),
                    created_at=node_data.get('created_at')
                )
            
            # Add edges
            neighbors = self.redis.smembers(f"edges:out:{current_id}")
            for neighbor in neighbors:
                edge_key = f"{self.edge_prefix}{current_id}:{neighbor}"
                edge_data = self.redis.hgetall(edge_key)
                
                if edge_data:
                    G.add_edge(
                        current_id,
                        neighbor,
                        edge_type=edge_data.get('edge_type'),
                        weight=float(edge_data.get('weight', 1.0)),
                        metadata=json.loads(edge_data.get('metadata', '{}'))
                    )
                    
                    if current_depth < depth:
                        to_visit.append((neighbor, current_depth + 1))
        
        return G