"""Similarity calculator service."""
from typing import Dict, List, Optional
import logging
import time

from src.domain.value_objects.similarity import SimilarityMetric
from src.application.services.similarity.strategies import ISimilarityStrategy

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Service for calculating text similarity using multiple strategies."""
    
    def __init__(self, strategies: Optional[Dict[str, ISimilarityStrategy]] = None):
        """Initialize with similarity strategies."""
        self._strategies = strategies or {}
        self._calculation_times = {}  # Track performance
    
    def add_strategy(self, metric: str, strategy: ISimilarityStrategy) -> None:
        """Add a new similarity strategy."""
        self._strategies[metric] = strategy
        logger.info(f"Added similarity strategy: {metric}")
    
    def calculate_similarity(
        self, 
        text1: str, 
        text2: str, 
        metric: SimilarityMetric
    ) -> float:
        """Calculate similarity using specified metric."""
        strategy = self._strategies.get(metric.value)
        if not strategy:
            available = list(self._strategies.keys())
            raise ValueError(f"Unknown similarity metric: {metric}. Available: {available}")
        
        # Track calculation time
        start_time = time.time()
        
        try:
            result = strategy.calculate(text1, text2)
            
            # Track performance
            calc_time = time.time() - start_time
            self._calculation_times[metric.value] = calc_time
            logger.debug(f"{metric.value} calculation took {calc_time:.3f}s")
            
            return result
        except Exception as e:
            logger.error(f"Error calculating {metric.value} similarity: {e}")
            raise
    
    def calculate_all_similarities(
        self, 
        text1: str, 
        text2: str
    ) -> Dict[str, float]:
        """Calculate similarity using all available metrics."""
        results = {}
        
        # Log input for debugging
        logger.debug(f"Calculating all similarities for:")
        logger.debug(f"  Text1: '{text1[:100]}...'")
        logger.debug(f"  Text2: '{text2[:100]}...'")
        
        for metric, strategy in self._strategies.items():
            try:
                start_time = time.time()
                
                # Calculate similarity
                score = strategy.calculate(text1, text2)
                results[strategy.get_metric_name()] = score
                
                # Track performance
                calc_time = time.time() - start_time
                self._calculation_times[metric] = calc_time
                
                logger.debug(f"  {metric}: {score:.4f} (took {calc_time:.3f}s)")
                
            except Exception as e:
                logger.error(f"Error in {metric} calculation: {e}")
                results[strategy.get_metric_name()] = 0.0
        
        # Log summary
        logger.info(f"Similarity scores: {results}")
        
        return results
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available similarity metrics."""
        return [strategy.get_metric_name() for strategy in self._strategies.values()]
    
    def get_calculation_times(self) -> Dict[str, float]:
        """Get performance metrics for each strategy."""
        return self._calculation_times.copy()
    
    def get_most_similar_metric(self, text1: str, text2: str) -> tuple[str, float]:
        """Find which metric shows highest similarity."""
        similarities = self.calculate_all_similarities(text1, text2)
        if not similarities:
            return None, 0.0
        
        max_metric = max(similarities.items(), key=lambda x: x[1])
        return max_metric
    
    def get_consensus_similarity(self, text1: str, text2: str, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted average of all similarity metrics."""
        similarities = self.calculate_all_similarities(text1, text2)
        
        if not similarities:
            return 0.0
        
        # Default equal weights if not provided
        if weights is None:
            weights = {metric: 1.0 for metric in similarities.keys()}
        
        # Calculate weighted average
        total_weight = sum(weights.get(metric, 0) for metric in similarities.keys())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(
            score * weights.get(metric, 0) 
            for metric, score in similarities.items()
        )
        
        return weighted_sum / total_weight