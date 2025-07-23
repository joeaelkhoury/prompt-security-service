"""Dependency injection for API - Fixed for in-memory storage."""
import threading
import os
from typing import Dict, Any

from src.core.config import Settings
from src.infrastructure.repositories.memory import InMemoryPromptRepository, InMemoryUserProfileRepository
from src.infrastructure.repositories.graph import NetworkXGraphRepository
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
            
            # Check if database is configured
            database_url = settings.database_url or os.getenv("DATABASE_URL", "")
            use_sql = "postgresql" in database_url
            
            if use_sql:
                try:
                    # Use SQL repositories
                    from src.infrastructure.database.connection import DatabaseConnection
                    from src.infrastructure.repositories.sql import SQLPromptRepository, SQLUserProfileRepository
                    from src.infrastructure.repositories.redis_graph import RedisGraphRepository
                    
                    print(f"Using SQL repositories with database: {database_url}")
                    self.db_connection = DatabaseConnection(settings)
                    session = self.db_connection.get_session()
                    self.prompt_repo = SQLPromptRepository(session)
                    self.user_repo = SQLUserProfileRepository(session)
                    
                    # Use Redis graph if available
                    if hasattr(self.db_connection, 'redis_client'):
                        self.graph_repo = RedisGraphRepository(self.db_connection.redis_client)
                    else:
                        self.graph_repo = NetworkXGraphRepository()
                except Exception as e:
                    print(f"Failed to initialize SQL repositories: {e}")
                    print("Falling back to in-memory repositories")
                    # Fallback to in-memory
                    self.prompt_repo = InMemoryPromptRepository()
                    self.user_repo = InMemoryUserProfileRepository()
                    self.graph_repo = NetworkXGraphRepository()
            else:
                # Use in-memory repositories
                print("Using in-memory repositories")
                self.prompt_repo = InMemoryPromptRepository()
                self.user_repo = InMemoryUserProfileRepository()
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
