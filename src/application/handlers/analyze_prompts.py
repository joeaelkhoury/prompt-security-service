"""Handler for analyze prompts command."""
import logging
from typing import List, Dict, Any
from datetime import datetime

from src.application.commands.analyze_prompts import AnalyzePromptsCommand, AnalyzePromptsResult
from src.application.commands.base import ICommandHandler
from src.domain.entities.prompt import Prompt, PromptStatus
from src.domain.entities.user import UserProfile
from src.domain.entities.graph import GraphNode, GraphEdge
from src.domain.repositories.interfaces import (
    IPromptRepository, IUserProfileRepository, IGraphRepository
)
from src.application.services.sanitization.sanitizer import ISanitizer
from src.application.services.similarity.calculator import SimilarityCalculator
from src.application.services.agents.orchestrator import AgentOrchestrator
from src.infrastructure.llm.factory import ILLMService
from src.core.constants import AgentRecommendation

logger = logging.getLogger(__name__)


class AnalyzePromptsHandler(ICommandHandler):
    """Handler for analyzing prompts for similarity and security."""
    
    def __init__(
        self,
        prompt_repo: IPromptRepository,
        user_repo: IUserProfileRepository,
        graph_repo: IGraphRepository,
        input_sanitizer: ISanitizer,
        output_sanitizer: ISanitizer,
        similarity_calculator: SimilarityCalculator,
        agent_orchestrator: AgentOrchestrator,
        llm_service: ILLMService
    ):
        """Initialize with dependencies."""
        self._prompt_repo = prompt_repo
        self._user_repo = user_repo
        self._graph_repo = graph_repo
        self._input_sanitizer = input_sanitizer
        self._output_sanitizer = output_sanitizer
        self._similarity_calculator = similarity_calculator
        self._agent_orchestrator = agent_orchestrator
        self._llm_service = llm_service
    
    def handle(self, command: AnalyzePromptsCommand) -> AnalyzePromptsResult:
        """Handle the analyze prompts command."""
        # Validate command
        is_valid, error_msg = command.validate()
        if not is_valid:
            return AnalyzePromptsResult(
                success=False,
                prompt1_id="",
                prompt2_id="",
                similarity_scores={},
                is_similar=False,
                error_message=error_msg
            )
        
        try:
            # 1. Get or create user profile
            user_profile = self._user_repo.create_if_not_exists(command.user_id)
            logger.info(f"Processing request for user: {command.user_id}")
            
            # Add user node to graph
            user_node = GraphNode(
                id=command.user_id,
                node_type='user',
                data={
                    'reputation': user_profile.reputation_score,
                    'total_prompts': user_profile.total_prompts
                }
            )
            self._graph_repo.add_node(user_node)
            logger.info(f"Added user node to graph: {command.user_id}")
            
            # 2. Sanitize input prompts
            sanitized1, issues1 = self._input_sanitizer.sanitize(command.prompt1_text)
            sanitized2, issues2 = self._input_sanitizer.sanitize(command.prompt2_text)
            
            all_issues = issues1 + issues2
            logger.info(f"Sanitization issues found: {len(all_issues)}")
            
            # 3. Create prompt entities
            prompt1 = Prompt(
                user_id=command.user_id,
                content=command.prompt1_text,
                sanitized_content=sanitized1
            )
            
            prompt2 = Prompt(
                user_id=command.user_id,
                content=command.prompt2_text,
                sanitized_content=sanitized2
            )
            
            # Set initial status based on sanitization
            if issues1:
                prompt1.status = PromptStatus.SUSPICIOUS
            if issues2:
                prompt2.status = PromptStatus.SUSPICIOUS
            
            # Save prompts
            self._prompt_repo.save(prompt1)
            self._prompt_repo.save(prompt2)
            
            # Add prompt nodes to graph
            for prompt, issues in [(prompt1, issues1), (prompt2, issues2)]:
                prompt_node = GraphNode(
                    id=prompt.id,
                    node_type='prompt',
                    data={
                        'content': prompt.sanitized_content[:100],  # First 100 chars
                        'user_id': prompt.user_id,
                        'status': prompt.status.value,
                        'has_issues': len(issues) > 0,
                        'timestamp': prompt.timestamp.isoformat()
                    }
                )
                self._graph_repo.add_node(prompt_node)
                logger.info(f"Added prompt node to graph: {prompt.id}")
                
                # Add edge from user to prompt
                user_edge = GraphEdge(
                    source_id=command.user_id,
                    target_id=prompt.id,
                    edge_type='submitted',
                    metadata={
                        'timestamp': datetime.utcnow().isoformat(),
                        'has_issues': len(issues) > 0
                    }
                )
                self._graph_repo.add_edge(user_edge)
            
            # 4. Calculate similarity scores
            similarity_scores = self._similarity_calculator.calculate_all_similarities(
                sanitized1, sanitized2
            )
            
            # Add similarity edge if prompts are similar
            max_score = max(similarity_scores.values()) if similarity_scores else 0
            is_similar = max_score >= command.similarity_threshold
            
            if is_similar:
                similarity_edge = GraphEdge(
                    source_id=prompt1.id,
                    target_id=prompt2.id,
                    edge_type='similar_to',
                    weight=max_score,
                    metadata={'scores': similarity_scores}
                )
                self._graph_repo.add_edge(similarity_edge)
                logger.info(f"Added similarity edge with score: {max_score}")
            
            # 5. Run agent analysis
            agent_analysis = self._agent_orchestrator.analyze_prompts(
                prompt1=prompt1,
                prompt2=prompt2,
                similarity_scores=similarity_scores,
                sanitization_issues=all_issues
            )
            
            # 6. Determine if LLM call should be made
            allow_llm = self._should_allow_llm(agent_analysis, all_issues)
            
            # 7. Call LLM if allowed
            llm_response = None
            if allow_llm:
                try:
                    combined_prompt = f"Prompt 1: {sanitized1}\n\nPrompt 2: {sanitized2}"
                    llm_response = self._llm_service.generate_response(combined_prompt)
                    
                    # Sanitize output
                    llm_response, _ = self._output_sanitizer.sanitize(llm_response)
                except Exception as e:
                    logger.error(f"LLM call failed: {str(e)}")
            
            # 8. Update user profile based on result
            is_safe = allow_llm and len(all_issues) == 0
            user_profile.update_reputation(is_safe)
            
            # Update prompt status
            if not allow_llm:
                prompt1.status = PromptStatus.BLOCKED
                prompt2.status = PromptStatus.BLOCKED
            elif all_issues:
                prompt1.status = PromptStatus.SUSPICIOUS
                prompt2.status = PromptStatus.SUSPICIOUS
            else:
                prompt1.status = PromptStatus.SAFE
                prompt2.status = PromptStatus.SAFE
            
            # Save updated entities
            self._user_repo.save(user_profile)
            self._prompt_repo.save(prompt1)
            self._prompt_repo.save(prompt2)
            
            # Update nodes in graph with final status
            for prompt in [prompt1, prompt2]:
                self._graph_repo.add_node(GraphNode(
                    id=prompt.id,
                    node_type='prompt',
                    data={
                        'content': prompt.sanitized_content[:100],
                        'user_id': prompt.user_id,
                        'status': prompt.status.value,
                        'final_status': prompt.status.value,
                        'timestamp': prompt.timestamp.isoformat()
                    }
                ))
            
            # Log graph status
            logger.info(f"Graph analysis complete. Nodes and edges added for prompts: {prompt1.id}, {prompt2.id}")
            
            # 9. Build result
            explanation = self._build_explanation(
                all_issues, agent_analysis, allow_llm, is_similar
            )
            
            return AnalyzePromptsResult(
                success=True,
                prompt1_id=prompt1.id,
                prompt2_id=prompt2.id,
                similarity_scores=similarity_scores,
                is_similar=is_similar,
                llm_response=llm_response,
                agent_analysis=agent_analysis,
                explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Error handling analyze command: {str(e)}", exc_info=True)
            return AnalyzePromptsResult(
                success=False,
                prompt1_id="",
                prompt2_id="",
                similarity_scores={},
                is_similar=False,
                error_message=str(e)
            )
    
    def _should_allow_llm(
        self, 
        agent_analysis: Dict[str, Any], 
        sanitization_issues: List[str]
    ) -> bool:
        """Determine if LLM call should be allowed."""
        # Check for critical sanitization issues
        if sanitization_issues:
            for issue in sanitization_issues:
                if any(critical in issue.lower() for critical in ['sql', 'xss', 'injection']):
                    return False
        
        # Check agent recommendations
        findings = agent_analysis.get('findings', [])
        for finding in findings:
            if finding.get('recommendation') == AgentRecommendation.BLOCK.value:
                return False
        
        # Check decision agent specifically
        decision_agent = next(
            (f for f in findings if f.get('agent') == 'DecisionAgent'), 
            None
        )
        if decision_agent and not decision_agent.get('allow_llm_call', True):
            return False
        
        return True
    
    def _build_explanation(
        self,
        issues: List[str],
        agent_analysis: Dict[str, Any],
        allow_llm: bool,
        is_similar: bool
    ) -> str:
        """Build explanation for the analysis result."""
        parts = []
        
        if not allow_llm:
            parts.append("Prompts blocked due to security concerns.")
            
        if issues:
            parts.append(f"Security issues detected: {', '.join(issues[:3])}")
            
        if is_similar:
            parts.append("Prompts are similar based on threshold.")
        
        # Add agent insights
        findings = agent_analysis.get('findings', [])
        blocks = [f for f in findings if f.get('recommendation') == 'block']
        if blocks:
            parts.append(f"{len(blocks)} agents recommended blocking.")
        
        if not parts:
            parts.append("Prompts analyzed successfully. No security issues detected.")
        
        return " ".join(parts)