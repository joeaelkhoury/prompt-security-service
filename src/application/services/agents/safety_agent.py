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
        """Analyze prompt safety with better context awareness."""
        prompt1: Prompt = context.get('prompt1')
        prompt2: Prompt = context.get('prompt2')
        user_id = context.get('user_id')
        sanitization_issues = context.get('sanitization_issues', [])
        
        # Get user profile
        user_profile = self._user_repo.find_by_id(user_id)
        if not user_profile:
            user_profile = self._user_repo.create_if_not_exists(user_id)
        
        findings = {
            'agent': self.get_name(),
            'user_reputation': user_profile.reputation_score,
            'recent_violations': 0,
            'suspicious_patterns': [],
            'recommendation': AgentRecommendation.ALLOW.value
        }
        
        # Check recent violations
        recent_prompts = self._prompt_repo.find_recent_by_user(user_id, hours=1)
        violations = [p for p in recent_prompts if p.status == PromptStatus.BLOCKED]
        findings['recent_violations'] = len(violations)
        
        # Analyze patterns
        user_patterns = self._graph_repo.get_user_patterns(user_id)
        for pattern in user_patterns:
            if pattern.get('type') == PatternType.RAPID_FIRE_QUERIES.value:
                if pattern.get('count', 0) > 10:
                    findings['suspicious_patterns'].append(pattern['type'])
        
        # Make recommendation based on context
        critical_issues = [
            issue for issue in sanitization_issues 
            if any(critical in issue.lower() for critical in [
                'sql_injection',
                'xss_attack', 
                'prompt_injection',
                'data_exfiltration'
            ])
        ]
        
        # Check if the issues are actually legitimate
        legitimate_keywords = [
            'correlation matrix',
            'engagement metrics',
            'security audit',
            'compliance',
            'migration',
            'backup',
            'admin privileges',
            'security officer'
        ]
        
        # If the prompts contain legitimate business terms, be less strict
        prompt_text = f"{prompt1.content} {prompt2.content}".lower()
        has_legitimate_context = any(keyword in prompt_text for keyword in legitimate_keywords)
        
        # Decision logic with context awareness
        if user_profile.reputation_score < 0.3 and len(critical_issues) > 0:
            findings['recommendation'] = AgentRecommendation.BLOCK.value
        elif len(violations) > 5:
            findings['recommendation'] = AgentRecommendation.BLOCK.value
        elif len(critical_issues) > 1 and not has_legitimate_context:
            findings['recommendation'] = AgentRecommendation.INVESTIGATE.value
        elif len(critical_issues) > 2:
            findings['recommendation'] = AgentRecommendation.BLOCK.value
        elif has_legitimate_context and user_profile.reputation_score > 0.5:
            # Trust legitimate business queries from reputable users
            findings['recommendation'] = AgentRecommendation.ALLOW.value
        
        return findings
    
    def get_name(self) -> str:
        """Get agent name."""
        return "SafetyAgent"
