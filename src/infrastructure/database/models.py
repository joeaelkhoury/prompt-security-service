# src/infrastructure/database/models.py
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class UserProfileModel(Base):
    __tablename__ = 'user_profiles'
    
    user_id = Column(String(255), primary_key=True, index=True)
    reputation_score = Column(Float, default=1.0)
    total_prompts = Column(Integer, default=0)
    blocked_prompts = Column(Integer, default=0)
    suspicious_patterns = Column(JSON, default=list)
    last_activity = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prompts = relationship("PromptModel", back_populates="user")
    
    __table_args__ = (
        Index('idx_reputation', 'reputation_score'),
    )

class PromptModel(Base):
    __tablename__ = 'prompts'
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(255), ForeignKey('user_profiles.user_id'), index=True)
    content = Column(Text)
    sanitized_content = Column(Text)
    status = Column(String(50), index=True)
    safety_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("UserProfileModel", back_populates="prompts")
    similarities = relationship("SimilarityModel", foreign_keys="SimilarityModel.prompt1_id")
    
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

class SimilarityModel(Base):
    __tablename__ = 'similarities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt1_id = Column(String(36), ForeignKey('prompts.id'), index=True)
    prompt2_id = Column(String(36), ForeignKey('prompts.id'), index=True)
    metric = Column(String(50))
    score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_similarity_lookup', 'prompt1_id', 'prompt2_id'),
    )

# src/infrastructure/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
import redis
from src.core.config import Settings

class DatabaseConnection:
    def __init__(self, settings: Settings):
        # PostgreSQL for persistent storage
        self.engine = create_engine(
            settings.database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            echo=False
        )
        
        # Session factory
        session_factory = sessionmaker(bind=self.engine)
        self.SessionLocal = scoped_session(session_factory)
        
        # Redis for caching and graph storage
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=0,
            decode_responses=True,
            connection_pool=redis.ConnectionPool(
                host=settings.redis_host,
                port=settings.redis_port,
                max_connections=50
            )
        )
    
    def get_session(self):
        return self.SessionLocal()
    
    def close_session(self):
        self.SessionLocal.remove()