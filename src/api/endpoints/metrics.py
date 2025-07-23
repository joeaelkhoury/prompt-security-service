"""Metrics endpoints."""
from fastapi import APIRouter, HTTPException, Depends
import logging

from src.api.models import MetricsResponse
from src.api.dependencies import ServiceContainer, get_service_container
from src.domain.value_objects.similarity import SimilarityMetric


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    container: ServiceContainer = Depends(get_service_container)
):
    """Get service metrics."""
    try:
        metrics = container.get_metrics()
        
        return MetricsResponse(
            total_requests=metrics['total_requests'],
            total_users=metrics['total_users'],
            blocked_prompts=metrics['blocked_prompts'],
            average_similarity=0.0,  # Simplified for now
            available_metrics=metrics['available_metrics']
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similarity-metrics")
async def get_similarity_metrics():
    """Get available similarity metrics."""
    return {
        'metrics': [metric.value for metric in SimilarityMetric],
        'default': SimilarityMetric.COSINE.value,
        'descriptions': {
            SimilarityMetric.COSINE.value: "Cosine similarity using TF-IDF vectors",
            SimilarityMetric.JACCARD.value: "Jaccard similarity based on word sets",
            SimilarityMetric.LEVENSHTEIN.value: "Normalized Levenshtein distance",
            SimilarityMetric.EMBEDDING.value: "Similarity using LLM embeddings"
        }
    }