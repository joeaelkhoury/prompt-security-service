import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to headers
        request.state.request_id = request_id
        
        # Log request
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(f"Response {request_id}: {response.status_code} in {process_time:.3f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request {request_id} failed after {process_time:.3f}s: {str(e)}")
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client, max_requests: int = 100, window: int = 3600):
        super().__init__(app)
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, self.window)
            
            if current > self.max_requests:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": str(self.window)}
                )
        except Exception:
            # If Redis fails, allow request
            pass
        
        return await call_next(request)