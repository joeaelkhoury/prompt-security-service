"""Decision making agent."""
from typing import Dict, Any

from src.application.services.agents.base import ISecurityAgent
from src.domain.entities.prompt import Prompt
from src.domain.repositories.interfaces import IGraphRepository
from src.core.constants import AgentRecommendation


class DecisionAgent(ISecurityAgent):
    """Agent that makes final decision based on other agents' findings."""
    
    def __init__(self, graph_repo: IGraphRepository):
        """Initialize with graph repository."""
        self._graph_repo = graph_repo
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make final decision based on agent findings."""
        agent_findings = context.get('agent_findings', [])
        prompt: Prompt = context.get('prompt1')
        
        decision = {
            'agent': self.get_name(),
            'allow_llm_call': True,
            'confidence': 1.0,
            'reasoning': [],
            'graph_visualization': None,
            'recommendation': AgentRecommendation.ALLOW.value  # Default recommendation
        }
        
        # Aggregate recommendations
        recommendations = [f['recommendation'] for f in agent_findings if f.get('recommendation')]
        
        if AgentRecommendation.BLOCK.value in recommendations:
            decision['allow_llm_call'] = False
            decision['reasoning'].append("Blocked due to safety concerns")
            decision['confidence'] = 0.9
            decision['recommendation'] = AgentRecommendation.BLOCK.value
        elif recommendations.count(AgentRecommendation.INVESTIGATE.value) > 1:
            decision['allow_llm_call'] = False
            decision['reasoning'].append("Multiple agents flagged for investigation")
            decision['confidence'] = 0.8
            decision['recommendation'] = AgentRecommendation.INVESTIGATE.value
        elif AgentRecommendation.REVIEW.value in recommendations:
            # Allow but with lower confidence
            decision['confidence'] = 0.6
            decision['reasoning'].append("Allowed with caution due to review flags")
            decision['recommendation'] = AgentRecommendation.REVIEW.value
        else:
            # Default is allow
            decision['reasoning'].append("No security concerns detected")
            decision['recommendation'] = AgentRecommendation.ALLOW.value
        
        # Add pattern detection reasoning
        for finding in agent_findings:
            patterns = finding.get('patterns_detected', [])
            for pattern in patterns:
                if pattern.get('severity') == 'high':
                    decision['allow_llm_call'] = False
                    decision['reasoning'].append(
                        f"High severity pattern detected: {pattern.get('type')}"
                    )
                    decision['recommendation'] = AgentRecommendation.BLOCK.value
        
        # Generate simple graph visualization data
        if prompt:
            try:
                subgraph = self._graph_repo.get_subgraph(prompt.id, depth=2)
                decision['graph_visualization'] = {
                    'nodes': len(subgraph.nodes()),
                    'edges': len(subgraph.edges()),
                    'prompt_id': prompt.id
                }
            except:
                # If graph operations fail, continue without visualization
                pass
        
        return decision
    
    def get_name(self) -> str:
        """Get agent name."""
        return "DecisionAgent"