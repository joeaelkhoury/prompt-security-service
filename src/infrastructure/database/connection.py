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
