# Prompt Security Service API Documentation

## Base URL

```
http://localhost/
```

## Authentication

The API uses JWT Bearer token authentication. Most endpoints require authentication.

### Obtain Access Token

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secret"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Token

Include the token in the Authorization header:
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Endpoints

### 1. Health Check

Check service health status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

---

### 2. Analyze Prompts

Analyze two prompts for similarity and security threats.

```http
POST /analyze
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "user_id": "user123",
  "prompt1": "What is machine learning?",
  "prompt2": "Explain artificial intelligence",
  "similarity_metric": "cosine",
  "similarity_threshold": 0.7
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Unique user identifier |
| `prompt1` | string | Yes | First prompt (1-5000 chars) |
| `prompt2` | string | Yes | Second prompt (1-5000 chars) |
| `similarity_metric` | string | No | Metric: `cosine`, `jaccard`, `levenshtein`, `embedding` (default: `cosine`) |
| `similarity_threshold` | float | No | Threshold 0.0-1.0 (default: 0.7) |

**Response:**
```json
{
  "success": true,
  "prompt1_id": "550e8400-e29b-41d4-a716-446655440000",
  "prompt2_id": "550e8400-e29b-41d4-a716-446655440001",
  "similarity_scores": {
    "cosine": 0.85,
    "jaccard": 0.72,
    "levenshtein": 0.78,
    "embedding": 0.91
  },
  "is_similar": true,
  "llm_response": "These prompts are discussing related AI concepts...",
  "explanation": "Prompts are similar and safe for processing",
  "agent_findings": [
    {
      "agent": "SimilarityAgent",
      "recommendation": "allow",
      "confidence": 0.95
    },
    {
      "agent": "SafetyAgent",
      "recommendation": "allow",
      "confidence": 0.98
    }
  ],
  "timestamp": "2024-01-20T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Analysis successful
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid token
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Processing error

**Security Findings:**

If security threats are detected:
```json
{
  "success": false,
  "explanation": "Security threats detected: SQL injection pattern found",
  "agent_findings": [
    {
      "agent": "SafetyAgent",
      "recommendation": "block",
      "confidence": 0.99,
      "details": {
        "threats": ["sql_injection"],
        "patterns": ["DROP TABLE", "DELETE FROM"]
      }
    }
  ]
}
```

---

### 3. Get User Profile

Retrieve user security profile and statistics.

```http
GET /users/{user_id}/profile
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
{
  "user_id": "user123",
  "reputation_score": 0.95,
  "total_prompts": 150,
  "blocked_prompts": 2,
  "is_trusted": true,
  "patterns": [
    {
      "type": "normal_usage",
      "frequency": "high"
    }
  ],
  "last_activity": "2024-01-20T10:25:00Z"
}
```

---

### 4. Get Metrics

Retrieve service metrics.

```http
GET /metrics
```

**Response:**
```json
{
  "total_requests": 10542,
  "total_users": 234,
  "blocked_prompts": 89,
  "average_similarity": 0.72,
  "available_metrics": ["cosine", "jaccard", "levenshtein", "embedding"]
}
```

**Note:** Prometheus-formatted metrics are available at `/metrics` with `Accept: text/plain`.

---

### 5. Get Graph Visualization

Get graph data for visualization.

```http
GET /graph/visualization/{node_id}?depth=2
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Query Parameters:**
- `depth` - Graph traversal depth (default: 2, max: 5)

**Response:**
```json
{
  "nodes": [
    {
      "id": "user123",
      "type": "user",
      "data": {
        "reputation": 0.95
      }
    },
    {
      "id": "prompt_001",
      "type": "prompt",
      "data": {
        "status": "safe",
        "content": "What is AI?"
      }
    }
  ],
  "edges": [
    {
      "source": "user123",
      "target": "prompt_001",
      "type": "submitted",
      "weight": 1.0
    }
  ],
  "center_node": "user123"
}
```

---

### 6. Authentication Endpoints

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "secret"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:**
```json
{
  "username": "admin"
}
```

#### Register New User
```http
POST /auth/register
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword"
}
```

---

## Rate Limiting

- Default: 100 requests per hour per IP
- Analyze endpoint: 10 requests per minute per user

Exceeded limits return:
```http
429 Too Many Requests
Retry-After: 3600
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "timestamp": "2024-01-20T10:30:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Common error codes:
- `invalid_request` - Malformed request
- `authentication_required` - Missing auth token
- `invalid_token` - Expired or invalid token
- `permission_denied` - Insufficient permissions
- `not_found` - Resource not found
- `rate_limit_exceeded` - Too many requests
- `internal_error` - Server error

---

## Similarity Metrics

### Cosine Similarity
Uses TF-IDF vectors to measure angular similarity. Best for comparing document structure and word importance.

### Jaccard Similarity
Compares word sets. Best for short texts where word overlap matters.

### Levenshtein Similarity
Measures edit distance. Best for detecting typos or slight variations.

### Embedding Similarity
Uses neural embeddings from OpenAI. Best for semantic similarity regardless of wording.

---

## Security Patterns Detected

The service detects:
- **SQL Injection**: `DROP TABLE`, `UNION SELECT`, etc.
- **XSS Attacks**: `<script>`, event handlers
- **Prompt Injection**: Hidden instructions, role switching
- **Data Exfiltration**: Attempts to extract sensitive data
- **Profanity**: Inappropriate content
- **Personal Information**: SSN, phone numbers, emails

---

## WebSocket Events (Future)

Coming soon: Real-time analysis updates via WebSocket.

```javascript
ws://localhost/ws

// Subscribe to analysis updates
{
  "action": "subscribe",
  "user_id": "user123"
}

// Receive updates
{
  "event": "analysis_complete",
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "blocked",
  "reason": "sql_injection"
}
```

---

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post('http://localhost/auth/login', json={
    'username': 'admin',
    'password': 'secret'
})
token = response.json()['access_token']

# Analyze prompts
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost/analyze', 
    headers=headers,
    json={
        'user_id': 'test_user',
        'prompt1': 'What is AI?',
        'prompt2': 'Explain machine learning',
        'similarity_metric': 'embedding'
    }
)
print(response.json())
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('http://localhost/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'admin',
        password: 'secret'
    })
});
const {access_token} = await loginResponse.json();

// Analyze prompts
const response = await fetch('http://localhost/analyze', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_id: 'test_user',
        prompt1: 'What is AI?',
        prompt2: 'Explain machine learning',
        similarity_metric: 'embedding'
    })
});
console.log(await response.json());
```

### cURL
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}' \
  | jq -r .access_token)

# Analyze
curl -X POST http://localhost/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt1": "What is AI?",
    "prompt2": "Explain machine learning"
  }'
```

---

## API Versioning

Currently v1 (unversioned). Future versions will use:
- URL versioning: `/v2/analyze`
- Header versioning: `API-Version: 2`

---

## Support

For issues or questions:
- Check service health: `/health`
- View logs: `docker-compose logs`
- API documentation: `/docs` (Swagger UI)
- Alternative docs: `/redoc` (ReDoc)