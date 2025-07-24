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
            'created_at': node.created_at.isoformat() if hasattr(node.created_at, 'isoformat') else str(node.created_at)
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
            'weight': str(edge.weight),  # Convert to string for Redis
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
            # Handle bytes
            neighbor = neighbor.decode() if isinstance(neighbor, bytes) else neighbor
            edge_key = f"{self.edge_prefix}{prompt_id}:{neighbor}"
            edge_data = self.redis.hgetall(edge_key)
            
            # Handle bytes in edge data
            edge_type = edge_data.get(b'edge_type', edge_data.get('edge_type', b'')).decode() if isinstance(edge_data.get(b'edge_type', edge_data.get('edge_type')), bytes) else edge_data.get('edge_type', '')
            weight_str = edge_data.get(b'weight', edge_data.get('weight', b'0')).decode() if isinstance(edge_data.get(b'weight', edge_data.get('weight')), bytes) else edge_data.get('weight', '0')
            
            if edge_type == 'similar_to':
                weight = float(weight_str)
                if weight >= threshold:
                    similar.append(neighbor)
        
        return similar
    
    def get_user_patterns(self, user_id: str) -> List[Dict]:
        """Get user patterns from Redis."""
        patterns = []
        
        # Get user's prompts
        prompts = self.redis.smembers(f"edges:out:{user_id}")
        blocked_count = 0
        total_prompts = 0
        
        for prompt_id in prompts:
            # Handle bytes
            prompt_id = prompt_id.decode() if isinstance(prompt_id, bytes) else prompt_id
            node_key = f"{self.node_prefix}{prompt_id}"
            node_data = self.redis.hgetall(node_key)
            
            if node_data:
                # Handle bytes in node data
                node_type = node_data.get(b'node_type', node_data.get('node_type', b'')).decode() if isinstance(node_data.get(b'node_type', node_data.get('node_type')), bytes) else node_data.get('node_type', '')
                
                if node_type == 'prompt':
                    total_prompts += 1
                    data_str = node_data.get(b'data', node_data.get('data', b'{}')).decode() if isinstance(node_data.get(b'data', node_data.get('data')), bytes) else node_data.get('data', '{}')
                    data = json.loads(data_str)
                    if data.get('status') == 'blocked':
                        blocked_count += 1
        
        if total_prompts > 0:
            patterns.append({
                'type': 'user_activity',
                'severity': 'info',
                'total_prompts': total_prompts,
                'blocked_prompts': blocked_count
            })
            
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
        
        # Check if node exists, if not create default user node
        node_key = f"{self.node_prefix}{node_id}"
        if not self.redis.exists(node_key):
            # Create default user node
            default_node = {
                'id': node_id,
                'node_type': 'user',
                'data': json.dumps({'new_user': True, 'reputation': 1.0}),
                'created_at': datetime.utcnow().isoformat()
            }
            self.redis.hset(node_key, mapping=default_node)
        
        while to_visit:
            current_id, current_depth = to_visit.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            
            # Add node
            node_data = self.redis.hgetall(f"{self.node_prefix}{current_id}")
            if node_data:
                # Handle bytes responses from Redis
                node_id_str = node_data.get(b'id', node_data.get('id', current_id)).decode() if isinstance(node_data.get(b'id', node_data.get('id')), bytes) else node_data.get('id', current_id)
                node_type = node_data.get(b'node_type', node_data.get('node_type', b'')).decode() if isinstance(node_data.get(b'node_type', node_data.get('node_type')), bytes) else node_data.get('node_type', '')
                data_str = node_data.get(b'data', node_data.get('data', b'{}')).decode() if isinstance(node_data.get(b'data', node_data.get('data')), bytes) else node_data.get('data', '{}')
                created_at = node_data.get(b'created_at', node_data.get('created_at', b'')).decode() if isinstance(node_data.get(b'created_at', node_data.get('created_at')), bytes) else node_data.get('created_at', '')
                
                G.add_node(
                    current_id,
                    node_type=node_type,
                    data=json.loads(data_str),
                    created_at=created_at
                )
            
            # Get both outgoing and incoming edges
            out_neighbors = self.redis.smembers(f"edges:out:{current_id}")
            in_neighbors = self.redis.smembers(f"edges:in:{current_id}")
            
            # Process outgoing edges
            for neighbor in out_neighbors:
                neighbor = neighbor.decode() if isinstance(neighbor, bytes) else neighbor
                edge_key = f"{self.edge_prefix}{current_id}:{neighbor}"
                edge_data = self.redis.hgetall(edge_key)
                
                if edge_data:
                    # Handle bytes in edge data
                    edge_type = edge_data.get(b'edge_type', edge_data.get('edge_type', b'')).decode() if isinstance(edge_data.get(b'edge_type', edge_data.get('edge_type')), bytes) else edge_data.get('edge_type', '')
                    weight_str = edge_data.get(b'weight', edge_data.get('weight', b'1.0')).decode() if isinstance(edge_data.get(b'weight', edge_data.get('weight')), bytes) else edge_data.get('weight', '1.0')
                    metadata_str = edge_data.get(b'metadata', edge_data.get('metadata', b'{}')).decode() if isinstance(edge_data.get(b'metadata', edge_data.get('metadata')), bytes) else edge_data.get('metadata', '{}')
                    
                    G.add_edge(
                        current_id,
                        neighbor,
                        edge_type=edge_type,
                        weight=float(weight_str),
                        metadata=json.loads(metadata_str)
                    )
                    
                    if current_depth < depth:
                        to_visit.append((neighbor, current_depth + 1))
            
            # Process incoming edges
            for predecessor in in_neighbors:
                predecessor = predecessor.decode() if isinstance(predecessor, bytes) else predecessor
                edge_key = f"{self.edge_prefix}{predecessor}:{current_id}"
                edge_data = self.redis.hgetall(edge_key)
                
                if edge_data and predecessor not in visited:
                    # Handle bytes in edge data
                    edge_type = edge_data.get(b'edge_type', edge_data.get('edge_type', b'')).decode() if isinstance(edge_data.get(b'edge_type', edge_data.get('edge_type')), bytes) else edge_data.get('edge_type', '')
                    weight_str = edge_data.get(b'weight', edge_data.get('weight', b'1.0')).decode() if isinstance(edge_data.get(b'weight', edge_data.get('weight')), bytes) else edge_data.get('weight', '1.0')
                    metadata_str = edge_data.get(b'metadata', edge_data.get('metadata', b'{}')).decode() if isinstance(edge_data.get(b'metadata', edge_data.get('metadata')), bytes) else edge_data.get('metadata', '{}')
                    
                    # Add the predecessor node if not already in graph
                    if predecessor not in G:
                        pred_node_data = self.redis.hgetall(f"{self.node_prefix}{predecessor}")
                        if pred_node_data:
                            pred_node_type = pred_node_data.get(b'node_type', pred_node_data.get('node_type', b'')).decode() if isinstance(pred_node_data.get(b'node_type', pred_node_data.get('node_type')), bytes) else pred_node_data.get('node_type', '')
                            pred_data_str = pred_node_data.get(b'data', pred_node_data.get('data', b'{}')).decode() if isinstance(pred_node_data.get(b'data', pred_node_data.get('data')), bytes) else pred_node_data.get('data', '{}')
                            pred_created_at = pred_node_data.get(b'created_at', pred_node_data.get('created_at', b'')).decode() if isinstance(pred_node_data.get(b'created_at', pred_node_data.get('created_at')), bytes) else pred_node_data.get('created_at', '')
                            
                            G.add_node(
                                predecessor,
                                node_type=pred_node_type,
                                data=json.loads(pred_data_str),
                                created_at=pred_created_at
                            )
                    
                    # Add edge if not already in graph
                    if not G.has_edge(predecessor, current_id):
                        G.add_edge(
                            predecessor,
                            current_id,
                            edge_type=edge_type,
                            weight=float(weight_str),
                            metadata=json.loads(metadata_str)
                        )
                    
                    if current_depth < depth:
                        to_visit.append((predecessor, current_depth + 1))
        
        return G
