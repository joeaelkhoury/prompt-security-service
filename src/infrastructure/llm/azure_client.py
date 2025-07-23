"""Azure OpenAI client implementation."""
import os
from typing import List, Optional, Dict, Any, Union
import numpy as np
from openai import AzureOpenAI
from sklearn.metrics.pairwise import cosine_similarity
import base64
from pathlib import Path
import mimetypes
import threading

from src.core.exceptions import InfrastructureException
from src.core.config import Settings


class AzureOpenAIClient:
    """Azure OpenAI client with singleton pattern."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, settings: Settings):
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, settings: Settings):
        """Initialize Azure OpenAI client."""
        if not hasattr(self, 'initialized'):
            self.settings = settings
            self._validate_settings()
            
            self.client = AzureOpenAI(
                azure_endpoint=settings.azure_endpoint,
                api_key=settings.azure_api_key,
                api_version=settings.azure_api_version
            )
            
            self.initialized = True
    
    def _validate_settings(self) -> None:
        """Validate required settings."""
        if not self.settings.azure_api_key:
            raise InfrastructureException("Azure API key is required")
        if not self.settings.azure_endpoint:
            raise InfrastructureException("Azure endpoint is required")
        if not self.settings.azure_api_version:
            raise InfrastructureException("Azure API version is required")
    
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using Azure OpenAI."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.settings.azure_chat_deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise InfrastructureException(f"LLM generation failed: {str(e)}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector using Azure OpenAI."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.settings.azure_embedding_deployment
            )
            return response.data[0].embedding
        except Exception as e:
            raise InfrastructureException(f"Embedding generation failed: {str(e)}")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings."""
        emb1_array = np.array(embedding1).reshape(1, -1)
        emb2_array = np.array(embedding2).reshape(1, -1)
        
        similarity = cosine_similarity(emb1_array, emb2_array)
        return float(similarity[0][0])
    
    def analyze_image(
        self,
        text: str,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> str:
        """Analyze image with text prompt."""
        content = [{"type": "text", "text": text}]
        
        if image_path:
            base64_image = self._encode_image(image_path)
            mime_type, _ = mimetypes.guess_type(image_path)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
            })
        elif image_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })
        elif image_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
        
        try:
            response = self.client.chat.completions.create(
                model=self.settings.azure_chat_deployment,
                messages=[{"role": "user", "content": content}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            raise InfrastructureException(f"Image analysis failed: {str(e)}")
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        path = Path(image_path)
        if not path.exists():
            raise InfrastructureException(f"Image file not found: {image_path}")
        
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')