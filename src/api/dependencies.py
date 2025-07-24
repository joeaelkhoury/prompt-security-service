"""Dependency injection for API - Fixed for in-memory storage."""
import threading
import os
from typing import Dict, Any
import redis
import logging

from src.core.config import Settings
from src.infrastructure.repositories.memory import InMemoryPromptRepository, InMemoryUserProfileRepository
from src.infrastructure.repositories.graph import NetworkXGraphRepository
from src.infrastructure.repositories.redis_graph import RedisGraphRepository
from src.infrastructure.llm.factory import LLMServiceFactory
from src.application.services.sanitization.strategies import (
    SQLInjectionSanitizer, XSSSanitizer, ProfanitySanitizer,
    LengthLimitSanitizer, URLSanitizer, PersonalInfoSanitizer,DataExfiltrationSanitizer, PromptInjectionSanitizer
)
from src.application.services.sanitization.sanitizer import CompositeSanitizer
from src.application.services.similarity.strategies import (
    CosineSimilarityStrategy, JaccardSimilarityStrategy,
    LevenshteinSimilarityStrategy, EmbeddingSimilarityStrategy
)
from src.application.services.similarity.calculator import SimilarityCalculator
from src.application.services.agents.similarity_agent import SimilarityAgent
from src.application.services.agents.safety_agent import SafetyAgent
from src.application.services.agents.decision_agent import DecisionAgent
from src.application.services.agents.orchestrator import AgentOrchestrator
from src.application.handlers.analyze_prompts import AnalyzePromptsHandler
from src.domain.value_objects.similarity import SimilarityMetric


class ServiceContainer:
    """Service container for dependency injection."""
    
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
        """Initialize service container."""
        if not hasattr(self, 'initialized'):
            self.settings = settings
            self.request_count = 0
            
            # Initialize repositories
            print("Initializing repositories...")
            self.prompt_repo = InMemoryPromptRepository()
            self.user_repo = InMemoryUserProfileRepository()
            
            # Try to use Redis for graph storage
            try:
                redis_client = redis.Redis(
                    host='redis',  # Docker service name
                    port=6379,
                    db=0,
                    decode_responses=False  # Important: keep as bytes
                )
                redis_client.ping()
                print("Connected to Redis for graph persistence")
                self.graph_repo = RedisGraphRepository(redis_client)
                
                # Ensure test data exists
                self._ensure_test_data()
                
            except Exception as e:
                print(f"Redis not available, using in-memory graph: {e}")
                self.graph_repo = NetworkXGraphRepository()
            
            # Initialize LLM service
            self.llm_service = LLMServiceFactory.create(
                settings=settings,
                use_mock=False,
                use_cache=True,
                cache_size=100
            )
            
            # Initialize sanitizers
            self.input_sanitizer = self._create_input_sanitizer()
            self.output_sanitizer = self._create_output_sanitizer()
            
            # Initialize similarity calculator
            self.similarity_calculator = self._create_similarity_calculator()
            
            # Initialize agents
            self.agent_orchestrator = self._create_agent_orchestrator()
            
            # Initialize command handler
            self.analyze_handler = AnalyzePromptsHandler(
                prompt_repo=self.prompt_repo,
                user_repo=self.user_repo,
                graph_repo=self.graph_repo,
                input_sanitizer=self.input_sanitizer,
                output_sanitizer=self.output_sanitizer,
                similarity_calculator=self.similarity_calculator,
                agent_orchestrator=self.agent_orchestrator,
                llm_service=self.llm_service
            )
            
            self.initialized = True
    
    def _ensure_test_data(self):
        """Ensure test data exists in graph repository."""
        try:
            from src.domain.entities.graph import GraphNode, GraphEdge
            from datetime import datetime
            
            # Check if test user exists by trying to get its subgraph
            test_graph = self.graph_repo.get_subgraph("test_user_001", depth=0)
            
            # If graph is empty, add test data
            if len(test_graph.nodes()) == 0:
                print("Adding test data to graph repository...")
                
                # Add test user
                test_user = GraphNode(
                    id="test_user_001",
                    node_type="user",
                    data={"reputation": 0.85, "total_prompts": 5},
                    created_at=datetime.utcnow()
                )
                self.graph_repo.add_node(test_user)
                
                # Add test prompts
                for i in range(3):
                    prompt = GraphNode(
                        id=f"test_prompt_{i}",
                        node_type="prompt",
                        data={
                            "content": f"Test prompt {i}",
                            "status": "safe" if i < 2 else "blocked",
                            "user_id": "test_user_001"
                        },
                        created_at=datetime.utcnow()
                    )
                    self.graph_repo.add_node(prompt)
                    
                    # Add edge from user to prompt
                    edge = GraphEdge(
                        source_id="test_user_001",
                        target_id=f"test_prompt_{i}",
                        edge_type="submitted",
                        weight=1.0,
                        metadata={"test": True}
                    )
                    self.graph_repo.add_edge(edge)
                
                # Add similarity edge between prompts
                sim_edge = GraphEdge(
                    source_id="test_prompt_0",
                    target_id="test_prompt_1",
                    edge_type="similar_to",
                    weight=0.85,
                    metadata={"similarity_score": 0.85}
                )
                self.graph_repo.add_edge(sim_edge)
                
                print("Test data added successfully")
            else:
                print(f"Test data already exists: {len(test_graph.nodes())} nodes found")
                
        except Exception as e:
            print(f"Error ensuring test data: {e}")
    
    def _create_input_sanitizer(self) -> CompositeSanitizer:
        """
        Create comprehensive input sanitizer with all security strategies.
        
        Returns:
            CompositeSanitizer configured with all security detection strategies
        """
        strategies = [
            # SQL injection detection (both direct and natural language)
            SQLInjectionSanitizer(),
            
            # Cross-site scripting prevention
            XSSSanitizer(),
            
            # Data theft and exfiltration detection
            DataExfiltrationSanitizer(),
            
            # Prompt injection and jailbreak attempts
            PromptInjectionSanitizer(),
            
            # Personal information protection
            PersonalInfoSanitizer(),
            
            # Malicious URL detection
            URLSanitizer(),
            
            # Content filtering
            ProfanitySanitizer(),
            
            # Length limits for resource protection
            LengthLimitSanitizer(max_length=self.settings.max_prompt_length),
        ]
        
        return CompositeSanitizer(strategies)

    def _create_output_sanitizer(self) -> CompositeSanitizer:
        """
        Create output sanitizer for response cleaning.
        
        Returns:
            CompositeSanitizer configured for output sanitization
        """
        strategies = [
            # Remove any injected scripts from responses
            XSSSanitizer(),
            
            # Filter inappropriate content
            ProfanitySanitizer(),
            
            # Protect personal information in responses
            PersonalInfoSanitizer(),
        ]
        
        return CompositeSanitizer(strategies)
    
    def _create_similarity_calculator(self) -> SimilarityCalculator:
        """Create similarity calculator with all strategies."""
        calculator = SimilarityCalculator()
        
        # Add strategies
        calculator.add_strategy(
            SimilarityMetric.COSINE.value,
            CosineSimilarityStrategy()
        )
        calculator.add_strategy(
            SimilarityMetric.JACCARD.value,
            JaccardSimilarityStrategy()
        )
        calculator.add_strategy(
            SimilarityMetric.LEVENSHTEIN.value,
            LevenshteinSimilarityStrategy()
        )
        calculator.add_strategy(
            SimilarityMetric.EMBEDDING.value,
            EmbeddingSimilarityStrategy(self.llm_service)
        )
        
        return calculator
    
    def _create_agent_orchestrator(self) -> AgentOrchestrator:
        """Create agent orchestrator with all agents."""
        agents = [
            SimilarityAgent(self.graph_repo),
            SafetyAgent(self.user_repo, self.prompt_repo, self.graph_repo),
            DecisionAgent(self.graph_repo)
        ]
        return AgentOrchestrator(agents)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics - fixed for in-memory repositories."""
        # For InMemoryUserProfileRepository
        if hasattr(self.user_repo, '_profiles'):
            total_users = len(self.user_repo._profiles)
        else:
            # Fallback for SQL repository
            total_users = 0
            
        # For InMemoryPromptRepository
        if hasattr(self.prompt_repo, '_prompts'):
            blocked_prompts = sum(
                1 for p in self.prompt_repo._prompts.values()
                if p.status.value == "blocked"
            )
        else:
            # Fallback for SQL repository
            blocked_prompts = 0
        
        return {
            'total_requests': self.request_count,
            'total_users': total_users,
            'blocked_prompts': blocked_prompts,
            'available_metrics': self.similarity_calculator.get_available_metrics()
        }


# Singleton instance
_container_instance = None


def get_service_container() -> ServiceContainer:
    """Get or create service container."""
    global _container_instance
    if _container_instance is None:
        settings = Settings.from_env()
        _container_instance = ServiceContainer(settings)
    return _container_instance
