"""Safety analysis agent."""
from datetime import datetime
from typing import Dict, Any

from src.application.services.agents.base import ISecurityAgent
from src.domain.entities.prompt import Prompt, PromptStatus
from src.domain.entities.graph import GraphNode, GraphEdge
from src.domain.repositories.interfaces import (
    IUserProfileRepository, IPromptRepository, IGraphRepository
)
from src.core.constants import AgentRecommendation, PatternType


class SafetyAgent(ISecurityAgent):
    """Agent that analyzes prompt safety based on user history."""
    
    def __init__(
        self, 
        user_repo: IUserProfileRepository,
        prompt_repo: IPromptRepository,
        graph_repo: IGraphRepository
    ):
        """Initialize with repositories."""
        self._user_repo = user_repo
        self._prompt_repo = prompt_repo
        self._graph_repo = graph_repo
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prompt safety."""
        user_id = context.get('user_id')
        prompt: Prompt = context.get('prompt1')
        sanitization_issues = context.get('sanitization_issues', [])
        
        findings = {
            'agent': self.get_name(),
            'user_reputation': 1.0,
            'recent_violations': 0,
            'patterns_detected': [],
            'recommendation': AgentRecommendation.ALLOW.value
        }
        
        # Get or create user profile
        user_profile = self._user_repo.create_if_not_exists(user_id)
        findings['user_reputation'] = user_profile.reputation_score
        
        # Add user node to graph
        user_node = GraphNode(
            id=user_id,
            node_type='user',
            data={'reputation': user_profile.reputation_score}
        )
        self._graph_repo.add_node(user_node)
        
        # Link user to prompt
        edge = GraphEdge(
            source_id=user_id,
            target_id=prompt.id,
            edge_type='submitted',
            metadata={'timestamp': datetime.utcnow().isoformat()}
        )
        self._graph_repo.add_edge(edge)
        
        # Check recent violations
        recent_prompts = self._prompt_repo.find_recent_by_user(user_id, hours=24)
        violations = [p for p in recent_prompts if p.status == PromptStatus.BLOCKED]
        findings['recent_violations'] = len(violations)
        
        # Analyze patterns
        user_patterns = self._graph_repo.get_user_patterns(user_id)
        findings['patterns_detected'] = user_patterns
        
        # Make recommendation
        if sanitization_issues:
            findings['recommendation'] = AgentRecommendation.BLOCK.value
        elif findings['recent_violations'] > 3:
            findings['recommendation'] = AgentRecommendation.BLOCK.value
            findings['patterns_detected'].append({
                'type': PatternType.REPEATED_VIOLATIONS.value,
                'severity': 'high'
            })
        elif user_profile.reputation_score < 0.3:
            findings['recommendation'] = AgentRecommendation.REVIEW.value
        
        return findings
    
    def get_name(self) -> str:
        """Get agent name."""
        return "SafetyAgent"