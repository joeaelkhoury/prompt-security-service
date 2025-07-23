"""Similarity analysis agent."""
from typing import Dict, Any

from src.application.services.agents.base import ISecurityAgent
from src.domain.entities.prompt import Prompt
from src.domain.entities.graph import GraphNode, GraphEdge
from src.domain.repositories.interfaces import IGraphRepository
from src.core.constants import AgentRecommendation, PatternType


class SimilarityAgent(ISecurityAgent):
    """Agent that tracks and analyzes prompt similarities."""
    
    def __init__(self, graph_repo: IGraphRepository):
        """Initialize with graph repository."""
        self._graph_repo = graph_repo
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prompt similarities."""
        prompt1: Prompt = context.get('prompt1')
        prompt2: Prompt = context.get('prompt2')
        similarity_scores = context.get('similarity_scores', {})
        
        findings = {
            'agent': self.get_name(),
            'similar_prompts': [],
            'similarity_pattern': None,
            'recommendation': AgentRecommendation.ALLOW.value
        }
        
        # Add prompts to graph
        for prompt in [prompt1, prompt2]:
            node = GraphNode(
                id=prompt.id,
                node_type='prompt',
                data={
                    'content': prompt.sanitized_content,
                    'user_id': prompt.user_id,
                    'status': prompt.status.value
                }
            )
            self._graph_repo.add_node(node)
        
        # Add similarity edge if prompts are similar
        max_score = max(similarity_scores.values()) if similarity_scores else 0
        if max_score > 0.7:
            edge = GraphEdge(
                source_id=prompt1.id,
                target_id=prompt2.id,
                edge_type='similar_to',
                weight=max_score,
                metadata={'scores': similarity_scores}
            )
            self._graph_repo.add_edge(edge)
            
            # Check for similarity patterns
            similar_prompts = self._graph_repo.find_similar_prompts(prompt1.id, 0.7)
            findings['similar_prompts'] = similar_prompts
            
            if len(similar_prompts) > 5:
                findings['similarity_pattern'] = PatternType.EXCESSIVE_SIMILAR_PROMPTS.value
                findings['recommendation'] = AgentRecommendation.INVESTIGATE.value
        
        return findings
    
    def get_name(self) -> str:
        """Get agent name."""
        return "SimilarityAgent"