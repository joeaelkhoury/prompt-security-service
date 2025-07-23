"""In-memory implementations of repositories."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from src.domain.entities.prompt import Prompt
from src.domain.entities.user import UserProfile
from src.domain.repositories.interfaces import IPromptRepository, IUserProfileRepository


class InMemoryPromptRepository(IPromptRepository):
    """In-memory implementation of prompt repository."""
    
    def __init__(self):
        self._prompts: Dict[str, Prompt] = {}
    
    def save(self, prompt: Prompt) -> None:
        """Save a prompt to storage."""
        self._prompts[prompt.id] = prompt
    
    def find_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """Find a prompt by ID."""
        return self._prompts.get(prompt_id)
    
    def find_by_user(self, user_id: str, limit: int = 10) -> List[Prompt]:
        """Find prompts by user ID."""
        user_prompts = [p for p in self._prompts.values() if p.user_id == user_id]
        return sorted(user_prompts, key=lambda p: p.timestamp, reverse=True)[:limit]
    
    def find_recent_by_user(self, user_id: str, hours: int = 24) -> List[Prompt]:
        """Find recent prompts by user."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            p for p in self._prompts.values()
            if p.user_id == user_id and p.timestamp > cutoff
        ]


class InMemoryUserProfileRepository(IUserProfileRepository):
    """In-memory implementation of user profile repository."""
    
    def __init__(self):
        self._profiles: Dict[str, UserProfile] = {}
    
    def save(self, profile: UserProfile) -> None:
        """Save a user profile."""
        self._profiles[profile.user_id] = profile
    
    def find_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Find a user profile by ID."""
        return self._profiles.get(user_id)
    
    def create_if_not_exists(self, user_id: str) -> UserProfile:
        """Create profile if it doesn't exist."""
        if user_id not in self._profiles:
            self._profiles[user_id] = UserProfile(user_id=user_id)
        return self._profiles[user_id]