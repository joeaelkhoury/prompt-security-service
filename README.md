# 🛡️ Prompt Security Service

**Enterprise-grade AI/LLM Security Platform** - Protect your AI applications from prompt injection attacks using advanced graph-based intelligence and multi-agent analysis.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/prompt-security-service)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://docker.com)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange.svg)](LICENSE)

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Quick Start](#-quick-start)
3. [System Requirements](#-system-requirements)
4. [Installation Guide](#-installation-guide)
5. [Configuration](#-configuration)
6. [Using the Service](#-using-the-service)
7. [Architecture](#-architecture)
8. [API Documentation](#-api-documentation)
9. [Security Features](#-security-features)
10. [Monitoring & Metrics](#-monitoring--metrics)
11. [Testing](#-testing)
12. [Troubleshooting](#-troubleshooting)
13. [Production Deployment](#-production-deployment)
14. [Development Guide](#-development-guide)
15. [License](#-license)

<img width="1889" height="924" alt="image" src="https://github.com/user-attachments/assets/e4108c6a-0c42-4f28-a713-4267493b9478" />

<img width="2272" height="1369" alt="image" src="https://github.com/user-attachments/assets/b6ba75d2-aa49-4cb9-828e-008acea317d5" />

## 🎯 Overview

The Prompt Security Service is a comprehensive security solution that protects AI/LLM applications from various attack vectors including prompt injection, SQL injection, XSS, and data exfiltration attempts. Built with Domain-Driven Design principles, it provides real-time threat detection, user reputation tracking, and intelligent decision-making through a multi-agent system.

### 🚀 Key Features

- **🔍 Advanced Threat Detection**
  - SQL injection (direct and natural language variants)
  - Cross-site scripting (XSS) prevention
  - Prompt injection and context switching attacks
  - Data exfiltration attempts
  - Personal information leakage prevention

- **🧠 Intelligent Analysis**
  - Multiple similarity metrics (Cosine, Jaccard, Levenshtein, Semantic)
  - Graph-based pattern recognition
  - User reputation scoring
  - Multi-agent decision system

- **⚡ Production Ready**
  - Horizontal scaling with load balancing
  - Redis caching for performance
  - Prometheus/Grafana monitoring
  - Rate limiting protection

- **🏗️ Enterprise Architecture**
  - Domain-Driven Design (DDD)
  - Command/Handler pattern
  - Repository pattern
  - Clean architecture layers
  - Microservice ready

## 🏗️ Sequence

<div align="center">
  <img src="./diagrams/sequence.jpeg" alt="Sequence Overview" width="800">
</div>

<details>
<summary>Click to expand sequence diagram</summary>

![Detailed Sequence](./diagrams/sequence.jpeg)

</details>

## ⚡ Quick Start

Get the service running in under 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/prompt-security-service.git
cd prompt-security-service

# 2. Create environment file with your Azure OpenAI credentials
cat > .env << 'EOF'
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large
EOF

# 3. Start all services
docker-compose up -d

# 4. Verify installation
curl http://localhost/health

# 5. Open the web interface
# Visit http://localhost:8501 in your browser
```

## 💻 System Requirements

### Prerequisites
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 20GB available
- **OS**: Linux, macOS, or Windows with WSL2
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Python**: 3.11+ (for local development)
- **Poetry**: 1.5+ (optional, for dependency management)

### Recommended for Production
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 100GB SSD
- **Network**: 100Mbps+

### Required Accounts
- **Azure OpenAI** account with:
  - API access enabled
  - GPT-4 deployment (for chat)
  - Text-embedding-3-large deployment (for embeddings)
  - 
<img width="1259" height="1287" alt="image" src="https://github.com/user-attachments/assets/841819ee-7dd0-47db-8584-43ea8efd1bea" />

## 📦 Installation Guide

### Step 1: Prerequisites Check

```bash
# Verify Docker installation
docker --version  # Should be 20.10+
docker-compose --version  # Should be 2.0+

# Check available ports (Windows PowerShell)
netstat -an | findstr ":80 :8501 :3000 :9090"

# Check available ports (Linux/Mac)
sudo lsof -i :80,8501,3000,9090 || echo "Ports are available"

# Verify system resources
docker system info | grep -E "(CPUs|Total Memory)"
```

### Step 2: Azure OpenAI Setup

1. **Create Azure OpenAI Resource**
   - Go to [Azure Portal](https://portal.azure.com)
   - Search for "Azure OpenAI"
   - Create new resource
   - Deploy required models:
     - gpt-4o (or gpt-4)
     - text-embedding-3-large (or text-embedding-ada-002)

2. **Get Credentials**
   - Copy your API key from Keys and Endpoint section
   - Note your endpoint URL (format: https://YOUR-RESOURCE.openai.azure.com/)
   - Note your deployment names

### Step 3: Project Setup

```bash
# Clone repository
git clone https://github.com/yourusername/prompt-security-service.git
cd prompt-security-service

# Create .env file
cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
# Azure OpenAI Configuration (REQUIRED)
AZURE_OPENAI_API_KEY=your-actual-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large

# Database Configuration (Optional - defaults provided)
DATABASE_URL=postgresql://user:password@postgres:5432/prompt_security
REDIS_HOST=redis
REDIS_PORT=6379

# Application Settings
LOG_LEVEL=INFO
MAX_PROMPT_LENGTH=2000
SIMILARITY_THRESHOLD=0.7
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
EOF

# Edit .env with your actual Azure credentials
# Windows: notepad .env
# Mac/Linux: nano .env
```

### Step 4: Launch Services

```bash
# Build and start all services
docker-compose up -d --build

# Monitor startup progress
docker-compose logs -f

# Wait for "Application startup complete" message
# Press Ctrl+C to exit logs (services continue running)

# Verify all services are running
docker-compose ps

# Expected services:
# - postgres (database)
# - redis (cache)
# - nginx (load balancer)
# - streamlit (web UI)
# - prometheus (metrics)
# - grafana (dashboards)
```

### Step 5: Verify Installation

```bash
# Test API health
curl http://localhost/health
# Expected: {"status":"healthy","timestamp":"...","version":"1.0.0"}

# Open web interfaces:
# API Documentation: http://localhost/docs
# Streamlit UI: http://localhost:8501
# Grafana: http://localhost:3000 (login: admin/admin)
# Prometheus: http://localhost:9090
```

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| **Azure OpenAI Settings** |
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | ✅ Yes | - | `sk-...` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | ✅ Yes | - | `https://myresource.openai.azure.com/` |
| `AZURE_OPENAI_API_VERSION` | API version to use | ✅ Yes | - | `2024-02-15-preview` |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | Chat model deployment name | ✅ Yes | - | `gpt-4o` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` | Embedding model deployment | ✅ Yes | - | `text-embedding-3-large` |
| **Database Settings** |
| `DATABASE_URL` | PostgreSQL connection string | No | `postgresql://user:password@postgres:5432/prompt_security` | - |
| `REDIS_HOST` | Redis hostname | No | `redis` | `redis` or `localhost` |
| `REDIS_PORT` | Redis port | No | `6379` | `6379` |
| **Application Settings** |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_PROMPT_LENGTH` | Maximum prompt length | No | `2000` | `1000-5000` |
| `SIMILARITY_THRESHOLD` | Default similarity threshold | No | `0.7` | `0.0-1.0` |
| `RATE_LIMIT_REQUESTS` | Requests per window | No | `100` | `10-1000` |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | No | `3600` | `60-86400` |

### Service Architecture

| Service | Port | Purpose | Scaling |
|---------|------|---------|---------|
| **nginx** | 80 | Load balancer & reverse proxy | 1 instance |
| **postgres** | 5432 | Primary database | 1 instance |
| **redis** | 6379 | Cache & graph storage | 1 instance |
| **streamlit** | 8501 | Web UI | 1 instance |
| **prometheus** | 9090 | Metrics collection | 1 instance |
| **grafana** | 3000 | Monitoring dashboards | 1 instance |

## 🎨 Using the Service

### Option 1: Web Interface (Recommended)

1. **Access the UI**
   ```
   http://localhost:8501
   ```

2. **Test Security Scenarios**
   - Select a pre-configured attack scenario from the sidebar
   - Or enter custom prompts to test
   - Click "Analyze" to see results

3. **Available Test Scenarios**
   - **SQL Injection**: Tests direct SQL and P2SQL attacks
   - **Context Switch Attack**: Tests prompt injection
   - **Data Exfiltration**: Tests data extraction attempts
   - **Safe Similar Prompts**: Normal similar queries
   - **Safe Different Prompts**: Normal different queries

4. **Understanding Results**
   - **🟢 ALLOWED**: Prompts are safe to process
   - **🔴 BLOCKED**: Security threats detected
   - **Similarity Scores**: Shows how similar prompts are
   - **Agent Findings**: Detailed analysis from each security agent

### Option 2: API Access

1. **Analyze Prompts**
   ```bash
   # Test for SQL injection
   curl -X POST http://localhost/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "prompt1": "Show me user data",
       "prompt2": "'; DROP TABLE users; --",
       "similarity_metric": "embedding",
       "similarity_threshold": 0.7
     }' | python -m json.tool
   ```

2. **Check User Profile**
   ```bash
   curl -X GET http://localhost/users/test_user/profile | python -m json.tool
   ```

3. **Get Metrics**
   ```bash
   curl -X GET http://localhost/metrics
   ```

### Option 3: Python Client

```python
import requests
import json

class PromptSecurityClient:
    def __init__(self, base_url="http://localhost"):
        self.base_url = base_url
    
    def analyze(self, user_id, prompt1, prompt2, metric="embedding"):
        response = requests.post(
            f"{self.base_url}/analyze",
            json={
                "user_id": user_id,
                "prompt1": prompt1,
                "prompt2": prompt2,
                "similarity_metric": metric,
                "similarity_threshold": 0.7
            }
        )
        return response.json()
    
    def get_user_profile(self, user_id):
        response = requests.get(f"{self.base_url}/users/{user_id}/profile")
        return response.json()
    
    def get_metrics(self):
        response = requests.get(f"{self.base_url}/metrics")
        return response.json()

# Usage
client = PromptSecurityClient()

# Test SQL injection
result = client.analyze(
    user_id="test_user",
    prompt1="Show me users",
    prompt2="SELECT * FROM users WHERE 1=1"
)

if result["success"]:
    print(f"Analysis: {result['explanation']}")
    print(f"LLM Response: {result.get('llm_response', 'Blocked')}")
else:
    print(f"Error: {result}")
```

### Option 4: PowerShell Client

```powershell
# Analyze prompts
$analyzeBody = @{
    user_id = "test-user-001"
    prompt1 = "Show me all users"
    prompt2 = "SELECT * FROM users"
    similarity_metric = "cosine"
    similarity_threshold = 0.7
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost/analyze" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $analyzeBody

# Display results
$result | ConvertTo-Json -Depth 5

# Get metrics
Invoke-RestMethod -Uri "http://localhost/metrics"

# Get user profile
Invoke-RestMethod -Uri "http://localhost/users/test-user-001/profile"
```

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                             │
│                            (Nginx)                                │
└─────────────────┬───────────────────────┬───────────────────────┘
                  │                       │
        ┌─────────▼─────────┐   ┌────────▼────────┐
        │   API Service     │   │   Streamlit UI   │
        │    (FastAPI)      │   │   (Port 8501)    │
        └─────────┬─────────┘   └─────────────────┘
                  │
    ┌─────────────┴─────────────────────────┐
    │                                       │
┌───▼───────┐  ┌────────────┐  ┌───────────▼────────┐
│PostgreSQL │  │   Redis    │  │   Azure OpenAI     │
│(Database) │  │  (Cache)   │  │   (LLM Service)    │
└───────────┘  └────────────┘  └────────────────────┘
```

### Domain-Driven Design Layers

1. **API Layer** (`src/api/`)
   - REST endpoints
   - Request/response models
   - Rate limiting

2. **Application Layer** (`src/application/`)
   - Command handlers
   - Service orchestration
   - Business workflows
   - Agent coordination

3. **Domain Layer** (`src/domain/`)
   - Core entities (Prompt, User, Graph)
   - Business rules
   - Repository interfaces
   - Value objects

4. **Infrastructure Layer** (`src/infrastructure/`)
   - Database implementations
   - External service integrations
   - LLM client
   - Caching

### Security Analysis Pipeline

```
Input → Sanitization → Similarity Check → Agent Analysis → Decision → Output
  │           │               │                │              │         │
  ▼           ▼               ▼                ▼              ▼         ▼
Validate   Remove      Compare using      3 Agents      Allow/Block  Clean
          threats    4 algorithms        analyze                    response
```

### Multi-Agent System

1. **SimilarityAgent**
   - Analyzes prompt patterns
   - Tracks relationships in graph
   - Detects pattern matching

2. **SafetyAgent**
   - Evaluates user reputation
   - Checks violation history
   - Identifies suspicious behavior

3. **DecisionAgent**
   - Aggregates all findings
   - Makes final decision
   - Provides confidence score

## 📚 API Documentation

### Analysis Endpoints

#### Analyze Prompts
```http
POST /analyze
Content-Type: application/json

{
    "user_id": "user123",
    "prompt1": "First prompt text",
    "prompt2": "Second prompt text",
    "similarity_metric": "embedding",
    "similarity_threshold": 0.7
}
```

**Response:**
```json
{
    "success": true,
    "prompt1_id": "550e8400-e29b-41d4-a716-446655440000",
    "prompt2_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "similarity_scores": {
        "cosine": 0.82,
        "jaccard": 0.65,
        "levenshtein": 0.78,
        "embedding": 0.91
    },
    "is_similar": true,
    "llm_response": "Based on the analysis...",
    "explanation": "Prompts are similar. No security threats detected.",
    "agent_findings": [
        {
            "agent": "SimilarityAgent",
            "recommendation": "allow",
            "confidence": 0.95
        },
        {
            "agent": "SafetyAgent",
            "recommendation": "allow",
            "confidence": 0.88
        },
        {
            "agent": "DecisionAgent",
            "recommendation": "allow",
            "confidence": 0.92
        }
    ]
}
```

#### Get User Profile
```http
GET /users/{user_id}/profile
```

**Response:**
```json
{
    "user_id": "user123",
    "reputation_score": 0.95,
    "total_prompts": 150,
    "blocked_prompts": 3,
    "suspicious_patterns": ["sql_injection"],
    "last_activity": "2024-01-20T10:30:00Z"
}
```

### Monitoring Endpoints

#### Health Check
```http
GET /health
```

#### Service Metrics
```http
GET /metrics
```

#### Graph Visualization
```http
GET /graph/visualization/{node_id}?depth=2
```

### Similarity Metrics Explained

1. **Cosine Similarity**
   - Uses TF-IDF vectors
   - Best for document similarity
   - Range: 0-1 (1 = identical)

2. **Jaccard Similarity**
   - Compares word sets
   - Good for short texts
   - Range: 0-1

3. **Levenshtein Distance**
   - Character-level comparison
   - Detects typos/variations
   - Normalized to 0-1

4. **Embedding Similarity**
   - Semantic understanding via AI
   - Best overall accuracy
   - Range: 0-1

## 🔒 Security Features

### Attack Detection Capabilities

#### 1. SQL Injection
- **Direct SQL**: `'; DROP TABLE users; --`
- **P2SQL**: Natural language SQL commands
- **Union attacks**: `UNION SELECT * FROM passwords`

#### 2. Prompt Injection
- **Context switching**: "Ignore previous instructions"
- **Role playing**: "As an admin user..."
- **Hidden instructions**: Using special characters

#### 3. XSS Attacks
- **Script tags**: `<script>alert('XSS')</script>`
- **Event handlers**: `<img onerror="...">`
- **JavaScript URLs**: `javascript:void(0)`

#### 4. Data Exfiltration
- **Direct queries**: "Show all passwords"
- **Indirect extraction**: "What's in the user table?"
- **Social engineering**: "For debugging purposes..."

### Defense Mechanisms

1. **Input Sanitization**
   - HTML encoding
   - SQL parameter binding
   - URL validation
   - Personal info redaction

2. **Pattern Matching**
   - Regex-based detection
   - Blacklist checking
   - Anomaly detection

3. **Behavioral Analysis**
   - User reputation tracking
   - Rate limiting
   - Pattern recognition
   - Graph-based intelligence

4. **Output Filtering**
   - Response sanitization
   - Content validation
   - Information leakage prevention

## 📊 Monitoring & Metrics

### Grafana Dashboards

Access at `http://localhost:3000` (login: admin/admin)

**Available Dashboards:**
1. **Service Overview**
   - Request rates
   - Response times
   - Error rates
   - Active users

2. **Security Metrics**
   - Blocked attempts by type
   - User reputation distribution
   - Attack patterns over time
   - Top threatened endpoints

3. **System Performance**
   - CPU/Memory usage
   - Database performance
   - Cache hit rates
   - Queue lengths

### Prometheus Metrics

Key metrics exposed at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | Request latency |
| `prompt_analysis_duration_seconds` | Histogram | Analysis time |
| `blocked_prompts_total` | Counter | Blocked prompts by reason |
| `user_reputation_score` | Gauge | Current user reputation |
| `similarity_scores` | Histogram | Distribution of scores |
| `active_connections` | Gauge | Active connections |

## 🧪 Testing

### Running Tests

```bash
# With Docker
docker-compose exec streamlit pytest

# Run specific test category
docker-compose exec streamlit python -m tests.test_load security

# Run with coverage
docker-compose exec streamlit pytest --cov=src tests/
```

### Local Development Testing

```bash
# If using Poetry, first activate the environment
poetry shell

# Run all tests
pytest

# Run specific test file
pytest tests/test_prompts.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html to view coverage report

#Run test core security
pytest tests/test_core_security.py

# Run security tests
python tests/test_load.py security

# Run performance tests
python tests/test_load.py stress 100 10
```

### Test Categories

1. **Security Tests** (`tests/test_prompts.py`)
   - SQL injection scenarios
   - XSS attack patterns
   - Prompt injection attempts
   - Data exfiltration tests

2. **Performance Tests** (`tests/test_load.py`)
   ```bash
   # Run load test (100 users, 10 requests each)
   python tests/test_load.py stress 100 10
   ```

3. **Integration Tests**
   - API endpoint testing
   - Database operations
   - Cache functionality
   - External service mocking

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Azure OpenAI Connection Error
```
Error: "Invalid API key" or "Resource not found"
```

**Solution:**
```bash
# Verify your credentials in .env file
cat .env | grep AZURE

# Test connection directly (PowerShell)
$env:AZURE_OPENAI_ENDPOINT = "your-endpoint"
$env:AZURE_OPENAI_API_KEY = "your-key"

curl.exe -X POST "$env:AZURE_OPENAI_ENDPOINT/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview" `
  -H "api-key: $env:AZURE_OPENAI_API_KEY" `
  -H "Content-Type: application/json" `
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

#### 2. Services Won't Start
```
Error: "bind: address already in use"
```

**Solution:**
```bash
# Windows: Find and kill conflicting processes
netstat -ano | findstr :80
taskkill /PID <PID> /F

# Linux/Mac: Find and kill conflicting processes
sudo lsof -i :80 | grep LISTEN
sudo kill -9 <PID>

# Or change ports in docker-compose.yml
ports:
  - "8080:80"  # Change from 80 to 8080
```

#### 3. App Containers Not Running
```
Error: "502 Bad Gateway"
```

**Solution:**
```bash
# Check if app service is defined in docker-compose.yml
# Should have a service like:
services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/prompt_security
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 4. Database Connection Failed
```
Error: "could not connect to server"
```

**Solution:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Check database logs
docker-compose logs postgres
```

#### 5. Out of Memory
```
Error: "Container killed due to memory limit"
```

**Solution:**
```bash
# Check current usage
docker stats

# Increase Docker Desktop memory allocation
# Windows/Mac: Docker Desktop → Settings → Resources → Memory
# Linux: Update docker daemon.json
```

### Debug Mode

Enable detailed logging:

```bash
# Set in .env
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart

# View debug logs
docker-compose logs -f
```

### Getting Help

1. **Check Logs**
   ```bash
   # All services
   docker-compose logs
   
   # Specific service
   docker-compose logs streamlit
   ```

2. **Service Status**
   ```bash
   docker-compose ps
   ```

3. **Reset Everything**
   ```bash
   docker-compose down -v
   docker system prune -a
   docker-compose up -d
   ```

## 🚀 Production Deployment

### Pre-Production Checklist

- [ ] **Configuration**
  - [ ] Set production Azure OpenAI endpoints
  - [ ] Configure production database
  - [ ] Set up Redis persistence
  - [ ] Adjust rate limits
  
- [ ] **Monitoring**
  - [ ] Configure Grafana alerts
  - [ ] Set up log aggregation
  - [ ] Enable APM (Application Performance Monitoring)
  - [ ] Configure backup strategy
  
- [ ] **Testing**
  - [ ] Run full test suite
  - [ ] Perform load testing
  - [ ] Security testing
  - [ ] Disaster recovery testing

### Scaling for Production

#### Horizontal Scaling
```yaml
# docker-compose.prod.yml
services:
  app:
    image: prompt-security:latest
    deploy:
      replicas: 10
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

#### Database Optimization
```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET work_mem = '128MB';
SELECT pg_reload_conf();
```

#### Redis Configuration
```conf
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
appendonly yes
```

## 💻 Development Guide

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/prompt-security-service.git
cd prompt-security-service

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Set environment variables
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="text-embedding-3-large"

# Run locally
python -m src.main

# Or use uvicorn with auto-reload
uvicorn src.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000
```

### Working with Dependencies

```bash
# Add new dependency
poetry add fastapi

# Add development dependency
poetry add --group dev pytest

# Update dependencies
poetry update

# Show installed packages
poetry show

# Export requirements.txt (for Docker)
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Code Structure

```
src/
├── api/              # API Layer
│   ├── app.py       # FastAPI setup
│   ├── endpoints/   # Route handlers
│   └── models.py    # Pydantic models
├── application/      # Business Logic
│   ├── commands/    # Command objects
│   ├── handlers/    # Command handlers
│   └── services/    # Domain services
├── domain/          # Core Domain
│   ├── entities/    # Business entities
│   └── repositories/# Repository interfaces
├── infrastructure/  # External Services
│   ├── database/    # Database access
│   └── llm/        # AI integrations
└── core/           # Shared utilities
```

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions under 50 lines
- Write tests for new features
- Maintain 80%+ test coverage

## 📄 License

This project is licensed under the Apache License 2.0.

---

**Built with ❤️ by Joe El Khoury**

For support, please open an issue on GitHub.
