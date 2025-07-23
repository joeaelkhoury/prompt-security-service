from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.domain.entities.prompt import Prompt, PromptStatus
from src.domain.entities.user import UserProfile
from src.domain.repositories.interfaces import IPromptRepository, IUserProfileRepository
from src.infrastructure.database.models import PromptModel, UserProfileModel

class SQLPromptRepository(IPromptRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, prompt: Prompt) -> None:
        db_prompt = PromptModel(
            id=prompt.id,
            user_id=prompt.user_id,
            content=prompt.content,
            sanitized_content=prompt.sanitized_content,
            status=prompt.status.value,
            safety_score=prompt.safety_score,
            timestamp=prompt.timestamp
        )
        self._session.merge(db_prompt)
        self._session.commit()
    
    def find_by_id(self, prompt_id: str) -> Optional[Prompt]:
        db_prompt = self._session.query(PromptModel).filter_by(id=prompt_id).first()
        if not db_prompt:
            return None
        
        prompt = Prompt(
            user_id=db_prompt.user_id,
            content=db_prompt.content,
            id=db_prompt.id
        )
        prompt.sanitized_content = db_prompt.sanitized_content
        prompt.status = PromptStatus(db_prompt.status)
        prompt.safety_score = db_prompt.safety_score
        prompt.timestamp = db_prompt.timestamp
        return prompt
    
    def find_by_user(self, user_id: str, limit: int = 10) -> List[Prompt]:
        db_prompts = (self._session.query(PromptModel)
                     .filter_by(user_id=user_id)
                     .order_by(PromptModel.timestamp.desc())
                     .limit(limit)
                     .all())
        
        return [self._model_to_entity(p) for p in db_prompts]
    
    def find_recent_by_user(self, user_id: str, hours: int = 24) -> List[Prompt]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        db_prompts = (self._session.query(PromptModel)
                     .filter(and_(
                         PromptModel.user_id == user_id,
                         PromptModel.timestamp > cutoff
                     ))
                     .all())
        
        return [self._model_to_entity(p) for p in db_prompts]
    
    def _model_to_entity(self, model: PromptModel) -> Prompt:
        prompt = Prompt(user_id=model.user_id, content=model.content, id=model.id)
        prompt.sanitized_content = model.sanitized_content
        prompt.status = PromptStatus(model.status)
        prompt.safety_score = model.safety_score
        prompt.timestamp = model.timestamp
        return prompt

class SQLUserProfileRepository(IUserProfileRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, profile: UserProfile) -> None:
        db_profile = UserProfileModel(
            user_id=profile.user_id,
            reputation_score=profile.reputation_score,
            total_prompts=profile.total_prompts,
            blocked_prompts=profile.blocked_prompts,
            suspicious_patterns=profile.suspicious_patterns,
            last_activity=profile.last_activity
        )
        self._session.merge(db_profile)
        self._session.commit()
    
    def find_by_id(self, user_id: str) -> Optional[UserProfile]:
        db_profile = self._session.query(UserProfileModel).filter_by(user_id=user_id).first()
        if not db_profile:
            return None
        
        return UserProfile(
            user_id=db_profile.user_id,
            reputation_score=db_profile.reputation_score,
            total_prompts=db_profile.total_prompts,
            blocked_prompts=db_profile.blocked_prompts,
            suspicious_patterns=db_profile.suspicious_patterns,
            last_activity=db_profile.last_activity
        )
    
    def create_if_not_exists(self, user_id: str) -> UserProfile:
        profile = self.find_by_id(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.save(profile)
        return profile