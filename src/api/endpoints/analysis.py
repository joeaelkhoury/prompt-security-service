"""Prompt analysis endpoints."""
from fastapi import APIRouter, HTTPException, Depends
import logging

from src.api.models import PromptAnalysisRequest, PromptAnalysisResponse
from src.api.dependencies import ServiceContainer, get_service_container
from src.application.commands.analyze_prompts import AnalyzePromptsCommand


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=PromptAnalysisResponse)
async def analyze_prompts(
    request: PromptAnalysisRequest,
    container: ServiceContainer = Depends(get_service_container)
):
    """
    Analyze two prompts for similarity and security.
    
    This endpoint:
    1. Sanitizes both input prompts
    2. Calculates similarity using multiple metrics
    3. Runs security analysis using graph-based agents
    4. Calls LLM if prompts are similar and safe
    5. Returns sanitized response with analysis results
    """
    try:
        # Track request
        container.request_count += 1
        
        # Create command
        command = AnalyzePromptsCommand(
            user_id=request.user_id,
            prompt1_text=request.prompt1,
            prompt2_text=request.prompt2,
            similarity_metric=request.similarity_metric,
            similarity_threshold=request.similarity_threshold
        )
        
        # Handle command
        result = container.analyze_handler.handle(command)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        # Extract agent findings for response
        agent_findings = []
        if result.agent_analysis:
            for finding in result.agent_analysis.get('findings', []):
                agent_findings.append({
                    'agent': finding.get('agent'),
                    'recommendation': finding.get('recommendation'),
                    'confidence': finding.get('confidence', 1.0)
                })
        
        return PromptAnalysisResponse(
            success=result.success,
            prompt1_id=result.prompt1_id,
            prompt2_id=result.prompt2_id,
            similarity_scores=result.similarity_scores,
            is_similar=result.is_similar,
            llm_response=result.llm_response,
            explanation=result.explanation,
            agent_findings=agent_findings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    container: ServiceContainer = Depends(get_service_container)
):
    """Get user security profile."""
    try:
        profile = container.user_repo.find_by_id(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Get user patterns from graph
        patterns = container.graph_repo.get_user_patterns(user_id)
        
        return {
            'user_id': profile.user_id,
            'reputation_score': profile.reputation_score,
            'total_prompts': profile.total_prompts,
            'blocked_prompts': profile.blocked_prompts,
            'is_trusted': profile.is_trusted(),
            'patterns': patterns,
            'last_activity': profile.last_activity.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/visualization/{node_id}")
async def get_graph_visualization(
    node_id: str,
    depth: int = 2,
    container: ServiceContainer = Depends(get_service_container)
):
    """Get graph visualization data for a node."""
    try:
        subgraph = container.graph_repo.get_subgraph(node_id, depth)
        
        # Convert to visualization format
        nodes = []
        edges = []
        
        for node in subgraph.nodes(data=True):
            nodes.append({
                'id': node[0],
                'type': node[1].get('node_type', 'unknown'),
                'data': node[1].get('data', {})
            })
        
        for edge in subgraph.edges(data=True):
            edges.append({
                'source': edge[0],
                'target': edge[1],
                'type': edge[2].get('edge_type', 'unknown'),
                'weight': edge[2].get('weight', 1.0)
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'center_node': node_id
        }
    except Exception as e:
        logger.error(f"Error getting graph visualization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
