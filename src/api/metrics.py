from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
active_connections = Gauge('active_connections', 'Number of active connections')
prompt_analysis_duration = Histogram('prompt_analysis_duration_seconds', 'Prompt analysis duration')
blocked_prompts_total = Counter('blocked_prompts_total', 'Total blocked prompts', ['reason'])
similarity_score_histogram = Histogram('similarity_scores', 'Distribution of similarity scores', ['metric'])

# Metrics endpoint
async def metrics_endpoint():
    return Response(content=generate_latest(), media_type="text/plain")

# Decorator for tracking metrics
def track_metrics(endpoint: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = kwargs.get('request', {}).method if 'request' in kwargs else 'UNKNOWN'
            
            active_connections.inc()
            try:
                result = await func(*args, **kwargs)
                status = getattr(result, 'status_code', 200)
                request_count.labels(method=method, endpoint=endpoint, status=status).inc()
                return result
            except Exception as e:
                request_count.labels(method=method, endpoint=endpoint, status=500).inc()
                raise
            finally:
                duration = time.time() - start_time
                request_duration.labels(method=method, endpoint=endpoint).observe(duration)
                active_connections.dec()
        
        return wrapper
    return decorator