"""Similarity calculation strategies."""
from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import Levenshtein
import logging

from src.domain.value_objects.similarity import SimilarityMetric

logger = logging.getLogger(__name__)


class ISimilarityStrategy:
    """Interface for similarity calculation strategies."""
    
    def calculate(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        raise NotImplementedError
    
    def get_metric_name(self) -> str:
        """Get the name of the similarity metric."""
        raise NotImplementedError


class CosineSimilarityStrategy(ISimilarityStrategy):
    """Cosine similarity using TF-IDF vectors."""
    
    def __init__(self):
        """Initialize TF-IDF vectorizer with better parameters."""
        # Improved vectorizer with better preprocessing
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=None,  # Keep all words for security analysis
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=1000,
            sublinear_tf=True,  # Use log normalization
            use_idf=True
        )
    
    def calculate(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity."""
        try:
            # Handle empty texts
            if not text1.strip() or not text2.strip():
                return 1.0 if text1.strip() == text2.strip() else 0.0
            
            # Create corpus with both texts
            corpus = [text1, text2]
            
            # Fit and transform with improved vectorizer
            tfidf_matrix = self._vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            result = float(similarity_matrix[0][0])
            
            # Log for debugging
            logger.debug(f"Cosine similarity between '{text1[:50]}...' and '{text2[:50]}...': {result}")
            
            return result
        except Exception as e:
            logger.error(f"Error in cosine similarity calculation: {e}")
            return 0.0
    
    def get_metric_name(self) -> str:
        """Get metric name."""
        return SimilarityMetric.COSINE.value


class JaccardSimilarityStrategy(ISimilarityStrategy):
    """Jaccard similarity based on word sets."""
    
    def calculate(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity."""
        # Improved tokenization with punctuation removal
        import string
        
        # Remove punctuation and convert to lowercase
        translator = str.maketrans('', '', string.punctuation)
        clean_text1 = text1.translate(translator).lower()
        clean_text2 = text2.translate(translator).lower()
        
        # Create word sets
        words1 = set(clean_text1.split())
        words2 = set(clean_text2.split())
        
        # Handle empty sets
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        result = len(intersection) / len(union)
        
        # Log for debugging
        logger.debug(f"Jaccard similarity: {result}, Common words: {intersection}")
        
        return result
    
    def get_metric_name(self) -> str:
        """Get metric name."""
        return SimilarityMetric.JACCARD.value


class LevenshteinSimilarityStrategy(ISimilarityStrategy):
    """Normalized Levenshtein distance similarity."""
    
    def calculate(self, text1: str, text2: str) -> float:
        """Calculate Levenshtein similarity."""
        # Handle None or empty strings
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Calculate Levenshtein distance
        distance = Levenshtein.distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 1.0
        
        # Normalize to 0-1 range
        similarity = 1.0 - (distance / max_len)
        
        # Log for debugging
        logger.debug(f"Levenshtein distance: {distance}, max_len: {max_len}, similarity: {similarity}")
        
        return similarity
    
    def get_metric_name(self) -> str:
        """Get metric name."""
        return SimilarityMetric.LEVENSHTEIN.value


class EmbeddingSimilarityStrategy(ISimilarityStrategy):
    """Similarity using embeddings from LLM."""
    
    def __init__(self, llm_service):
        """Initialize with LLM service."""
        self._llm_service = llm_service
        self._embedding_cache = {}  # Simple cache for embeddings
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding with caching."""
        # Check cache first
        if text in self._embedding_cache:
            logger.debug(f"Using cached embedding for text: '{text[:50]}...'")
            return self._embedding_cache[text]
        
        # Get new embedding
        embedding = self._llm_service.get_embedding(text)
        
        # Cache it (limit cache size to prevent memory issues)
        if len(self._embedding_cache) < 1000:
            self._embedding_cache[text] = embedding
        
        return embedding
    
    def calculate(self, text1: str, text2: str) -> float:
        """Calculate embedding similarity."""
        try:
            # Handle empty texts
            if not text1.strip() or not text2.strip():
                return 1.0 if text1.strip() == text2.strip() else 0.0
            
            # Get embeddings with caching
            emb1 = self._get_embedding(text1)
            emb2 = self._get_embedding(text2)
            
            # Convert to numpy arrays
            emb1_array = np.array(emb1).reshape(1, -1)
            emb2_array = np.array(emb2).reshape(1, -1)
            
            # Calculate cosine similarity between embeddings
            similarity = cosine_similarity(emb1_array, emb2_array)
            result = float(similarity[0][0])
            
            # Log for debugging
            logger.debug(f"Embedding similarity between '{text1[:50]}...' and '{text2[:50]}...': {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in embedding similarity calculation: {e}")
            # Fallback to cosine similarity
            logger.warning("Falling back to cosine similarity due to embedding error")
            return CosineSimilarityStrategy().calculate(text1, text2)
    
    def get_metric_name(self) -> str:
        """Get metric name."""
        return SimilarityMetric.EMBEDDING.value