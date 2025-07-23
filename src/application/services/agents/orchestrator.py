"""Agent orchestrator for coordinating multiple agents."""
from typing import List, Dict, Any
from datetime import datetime

from src.application.services.agents.base import ISecurityAgent
from src.domain.entities.prompt import Prompt
from src.core.constants import AgentRecommendation

class AgentOrchestrator:
    """Orchestrates multiple agents for comprehensive analysis."""
    
    def __init__(self, agents: List[ISecurityAgent]):
        """Initialize with list of agents."""
        self._agents = agents
    
    def analyze_prompts(
        self,
        prompt1: Prompt,
        prompt2: Prompt,
        similarity_scores: Dict[str, float],
        sanitization_issues: List[str]
    ) -> Dict[str, Any]:
        """Run all agents and aggregate findings."""
        context = {
            'prompt1': prompt1,
            'prompt2': prompt2,
            'user_id': prompt1.user_id,
            'similarity_scores': similarity_scores,
            'sanitization_issues': sanitization_issues,
            'agent_findings': []
        }
        
        # Run each agent
        for agent in self._agents:
            try:
                findings = agent.analyze(context)
                context['agent_findings'].append(findings)
            except Exception as e:
                # Log error but continue with other agents
                context['agent_findings'].append({
                    'agent': agent.get_name(),
                    'error': str(e),
                    'recommendation': AgentRecommendation.REVIEW.value
                })
        
        # Final aggregated result
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'prompt_ids': [prompt1.id, prompt2.id],
            'findings': context['agent_findings'],
            'similarity_scores': similarity_scores,
            'sanitization_issues': sanitization_issues
        }