"""LLM service factory implementation."""
from typing import Optional
from abc import ABC, abstractmethod
from typing import List
import threading
from typing import Dict

from src.core.config import Settings
from src.infrastructure.llm.azure_client import AzureOpenAIClient


class ILLMService(ABC):
    """Interface for LLM services."""
    
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response from LLM."""
        pass
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text."""
        pass


class AzureLLMService(ILLMService):
    """Azure OpenAI implementation of LLM service."""
    
    def __init__(self, client: AzureOpenAIClient):
        """Initialize with Azure client."""
        self._client = client
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response using Azure OpenAI."""
        return self._client.generate_response(prompt, max_tokens)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector using Azure OpenAI."""
        return self._client.get_embedding(text)


class MockLLMService(ILLMService):
    """Mock LLM service for testing."""
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate mock response."""
        return f"Mock response to: {prompt[:50]}..."
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate mock embedding."""
        import numpy as np
        hash_val = hash(text)
        np.random.seed(abs(hash_val) % 2**32)
        return np.random.rand(1536).tolist()


class CachedLLMService(ILLMService):
    """Decorator for LLM service with caching."""
    
    def __init__(self, llm_service: ILLMService, cache_size: int = 100):
        """Initialize with underlying service and cache size."""
        self._service = llm_service
        self._response_cache: Dict[str, str] = {}
        self._embedding_cache: Dict[str, List[float]] = {}
        self._cache_size = cache_size
        self._lock = threading.Lock()
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response with caching."""
        cache_key = f"{prompt}:{max_tokens}"
        
        with self._lock:
            if cache_key in self._response_cache:
                return self._response_cache[cache_key]
        
        response = self._service.generate_response(prompt, max_tokens)
        
        with self._lock:
            if len(self._response_cache) >= self._cache_size:
                # Remove oldest entry (FIFO)
                oldest_key = next(iter(self._response_cache))
                del self._response_cache[oldest_key]
            
            self._response_cache[cache_key] = response
        
        return response
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding with caching."""
        with self._lock:
            if text in self._embedding_cache:
                return self._embedding_cache[text]
        
        embedding = self._service.get_embedding(text)
        
        with self._lock:
            if len(self._embedding_cache) >= self._cache_size:
                oldest_key = next(iter(self._embedding_cache))
                del self._embedding_cache[oldest_key]
            
            self._embedding_cache[text] = embedding
        
        return embedding


class LLMServiceFactory:
    """Factory for creating LLM service instances."""
    
    _instances = {}
    _lock = threading.Lock()
    
    @classmethod
    def create(
        cls,
        settings: Settings,
        use_mock: bool = False,
        use_cache: bool = True,
        cache_size: int = 100
    ) -> ILLMService:
        """Create appropriate LLM service instance."""
        key = f"{use_mock}_{use_cache}_{cache_size}"
        
        with cls._lock:
            if key not in cls._instances:
                if use_mock:
                    service = MockLLMService()
                else:
                    client = AzureOpenAIClient(settings)
                    service = AzureLLMService(client)
                
                if use_cache:
                    service = CachedLLMService(service, cache_size)
                
                cls._instances[key] = service
        
        return cls._instances[key]