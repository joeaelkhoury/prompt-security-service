# 🛡️ Prompt Security Service

A production-ready microservice for analyzing prompt similarity and detecting security threats in AI/LLM inputs using graph-based intelligence, multi-layered security analysis, and Domain-Driven Design principles.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-orange.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Core Components](#core-components)
- [Security Features](#security-features)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Development](#development)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Prompt Security Service is an advanced security system designed to protect AI/LLM applications from prompt injection attacks, including SQL injection, XSS, and sophisticated manipulation attempts. Built with Domain-Driven Design (DDD) principles, it provides enterprise-grade security through multiple analysis layers.

### Key Capabilities

- **Multi-Layer Security**: Combines rule-based detection, semantic analysis, and behavioral tracking
- **Graph Intelligence**: Builds knowledge graphs to detect attack patterns across users and time
- **Reputation System**: Tracks user behavior and adjusts security scrutiny accordingly
- **Real-time Analysis**: Processes prompts with multiple similarity metrics
- **Agent-Based Architecture**: Specialized agents analyze different security aspects
- **Production Ready**: Includes monitoring, scaling, authentication, and comprehensive testing

## ✨ Features

### Security Detection
- **SQL Injection Prevention**: Detects both direct SQL and natural language manipulation
- **XSS Protection**: Identifies and sanitizes cross-site scripting attempts
- **Prompt Injection Detection**: Catches context switching and jailbreak attempts
- **Data Exfiltration Prevention**: Blocks attempts to extract sensitive information
- **Pattern Recognition**: Learns and identifies evolving attack strategies

### Technical Features
- **Multiple Similarity Metrics**: Cosine, Jaccard, Levenshtein, and LLM embeddings
- **Sanitization Strategies**: SQL, XSS, profanity, URL, and personal info filters
- **Graph-Based Tracking**: NetworkX-powered relationship analysis
- **Caching System**: Redis-based caching for improved performance
- **Async Processing**: High-performance FastAPI implementation
- **JWT Authentication**: Secure API access control
- **Horizontal Scaling**: Load-balanced architecture with Nginx

### Monitoring & Observability
- **Prometheus Metrics**: Real-time performance tracking
- **Grafana Dashboards**: Visual monitoring and alerts
- **Health Checks**: Service availability monitoring
- **Audit Logging**: Comprehensive activity tracking

## 🏗️ Architecture

### Domain-Driven Design Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                              │
│  (FastAPI, REST endpoints, Authentication, Validation)        │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                          │
│  (Commands, Handlers, Services, Agents, Orchestration)       │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                             │
│  (Entities, Value Objects, Repository Interfaces, Rules)     │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                        │
│  (Database, Cache, LLM Services, External Integrations)      │
└─────────────────────────────────────────────────────────────┘
```

### Security Analysis Pipeline

```
User Input → Input Sanitization → Similarity Calculation → Agent Analysis → Decision → Output Sanitization → Response
     ↓              ↓                      ↓                     ↓              ↓              ↓              ↓
 Validation    SQL/XSS/PII         Multiple Metrics      Graph Analysis    Allow/Block    Clean Output    API/LLM
```

### Multi-Agent System

1. **SimilarityAgent**: Tracks prompt relationships and patterns in the graph
2. **SafetyAgent**: Analyzes user behavior, reputation, and violation history
3. **DecisionAgent**: Aggregates findings and makes final security decisions
4. **AgentOrchestrator**: Coordinates all agents and handles errors gracefully

### Key Design Patterns

- **Repository Pattern**: Abstracts data access behind interfaces
- **Command Pattern**: Encapsulates business operations
- **Strategy Pattern**: Flexible similarity metrics and sanitization
- **Factory Pattern**: LLM service creation
- **Singleton Pattern**: Service container management
- **Composite Pattern**: Multi-strategy sanitization

## 📁 Project Structure

```
prompt-security-service/
├── src/
│   ├── api/                    # REST API Layer
│   │   ├── app.py             # FastAPI application setup
│   │   ├── endpoints/         # API route handlers
│   │   │   ├── health.py      # Health check endpoints
│   │   │   ├── analysis.py    # Core analysis endpoints
│   │   │   ├── metrics.py     # Metrics endpoints
│   │   │   └── auth.py        # Authentication endpoints
│   │   ├── models.py          # Request/response models
│   │   └── dependencies.py    # Dependency injection
│   │
│   ├── application/           # Business Logic Layer
│   │   ├── commands/          # Command pattern implementation
│   │   │   ├── base.py        # Command interfaces
│   │   │   └── analyze_prompts.py  # Analysis command
│   │   ├── handlers/          # Command handlers
│   │   │   └── analyze_prompts.py  # Analysis handler
│   │   └── services/          # Domain services
│   │       ├── agents/        # Security analysis agents
│   │       │   ├── base.py    # Agent interface
│   │       │   ├── similarity_agent.py
│   │       │   ├── safety_agent.py
│   │       │   ├── decision_agent.py
│   │       │   └── orchestrator.py
│   │       ├── sanitization/  # Input/output sanitizers
│   │       │   ├── strategies.py  # Sanitization strategies
│   │       │   └── sanitizer.py   # Composite sanitizer
│   │       └── similarity/    # Similarity calculators
│   │           ├── strategies.py  # Similarity algorithms
│   │           └── calculator.py  # Similarity calculator
│   │
│   ├── domain/               # Domain Models (DDD)
│   │   ├── entities/         # Business entities
│   │   │   ├── prompt.py     # Prompt entity
│   │   │   ├── user.py       # User profile entity
│   │   │   └── graph.py      # Graph entities
│   │   ├── repositories/     # Repository interfaces
│   │   │   └── interfaces.py # Repository contracts
│   │   └── value_objects/    # Value objects
│   │       └── similarity.py # Similarity value objects
│   │
│   ├── infrastructure/       # External Integrations
│   │   ├── database/         # Database layer
│   │   │   ├── models.py     # SQLAlchemy models
│   │   │   └── connection.py # Database connection
│   │   ├── llm/             # LLM service implementations
│   │   │   ├── azure_client.py  # Azure OpenAI client
│   │   │   └── factory.py       # LLM service factory
│   │   └── repositories/     # Repository implementations
│   │       ├── memory.py     # In-memory repositories
│   │       ├── sql.py        # SQL repositories
│   │       ├── graph.py      # Graph repository
│   │       └── redis_graph.py # Redis graph repository
│   │
│   └── core/                # Shared Utilities
│       ├── config.py        # Configuration management
│       ├── constants.py     # Application constants
│       └── exceptions.py    # Custom exceptions
│
├── tests/
│   ├── test_prompts.py      # Attack scenario definitions
│   └── test_load.py         # Load testing framework
│
├── alembic/                 # Database migrations
│   ├── versions/            # Migration files
│   └── env.py              # Alembic configuration
│
├── lib/                     # Frontend libraries
│   ├── vis-9.1.2/          # Graph visualization
│   └── tom-select/         # UI components
│
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container definition
├── frontend.py             # Streamlit UI
├── frontend.html           # Web dashboard
├── pyproject.toml          # Poetry dependencies
├── requirements.txt        # Python dependencies
├── prometheus.yml          # Monitoring configuration
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
└── .pre-commit-config.yaml # Pre-commit hooks
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Azure OpenAI API credentials
- 8GB RAM minimum
- Ports available: 80, 3000, 8501, 9090

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/prompt-security-service.git
cd prompt-security-service
```

### 2. Configure Environment

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required Azure OpenAI Settings
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# Optional Settings (defaults provided)
DATABASE_URL=postgresql://user:password@postgres:5432/prompt_security
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET_KEY=your-secret-key-change-in-production
LOG_LEVEL=INFO
```

### 3. Start the Service

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
curl http://localhost/health
```

### 4. Access the Services

- **API Documentation**: http://localhost/docs
- **Streamlit UI**: http://localhost:8501
- **Grafana Dashboards**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### 5. Get Authentication Token

```bash
# Login to get JWT token
curl -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'

# Use the token in requests
curl http://localhost/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt1": "Show me all users",
    "prompt2": "SELECT * FROM users",
    "similarity_metric": "cosine",
    "similarity_threshold": 0.7
  }'
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes | - |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes | - |
| `AZURE_OPENAI_API_VERSION` | API version | Yes | - |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | Chat model deployment | Yes | - |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` | Embedding model deployment | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | No | postgresql://user:password@localhost/prompt_security |
| `REDIS_HOST` | Redis hostname | No | localhost |
| `REDIS_PORT` | Redis port | No | 6379 |
| `JWT_SECRET_KEY` | JWT signing key | No | Generated |
| `LOG_LEVEL` | Logging level | No | INFO |
| `MAX_PROMPT_LENGTH` | Maximum prompt length | No | 2000 |
| `SIMILARITY_THRESHOLD` | Default similarity threshold | No | 0.7 |
| `RATE_LIMIT_REQUESTS` | Rate limit requests per window | No | 100 |
| `RATE_LIMIT_WINDOW` | Rate limit window (seconds) | No | 3600 |

### Docker Services

The `docker-compose.yml` defines these services:

| Service | Purpose | Port | Scaling |
|---------|---------|------|---------|
| app1, app2, app3 | API instances | Internal | Horizontal |
| nginx | Load balancer | 80 | Single |
| postgres | Primary database | 5432 | Single |
| redis | Cache & graph | 6379 | Single |
| prometheus | Metrics | 9090 | Single |
| grafana | Dashboards | 3000 | Single |
| streamlit | Web UI | 8501 | Single |

## 📚 API Documentation

### Authentication

The API uses JWT bearer token authentication.

#### Login
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
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### Core Endpoints

#### Analyze Prompts
```http
POST /analyze
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
    "user_id": "user123",
    "prompt1": "Show me all users in the system",
    "prompt2": "SELECT * FROM users",
    "similarity_metric": "cosine",
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
    "llm_response": "The database contains user information...",
    "explanation": "Prompts are similar based on threshold. Security issues detected: sql_injection.",
    "agent_findings": [
        {
            "agent": "SimilarityAgent",
            "similar_prompts": ["uuid1", "uuid2"],
            "recommendation": "allow"
        },
        {
            "agent": "SafetyAgent",
            "user_reputation": 0.85,
            "recommendation": "investigate"
        },
        {
            "agent": "DecisionAgent",
            "final_decision": "block",
            "confidence": 0.92
        }
    ],
    "timestamp": "2024-01-20T10:30:00Z"
}
```

#### Get User Profile
```http
GET /users/{user_id}/profile
Authorization: Bearer YOUR_TOKEN
```

#### Get Service Metrics
```http
GET /metrics
Authorization: Bearer YOUR_TOKEN
```

#### Health Check
```http
GET /health
```

### Rate Limiting

- Default: 100 requests per hour per user
- Headers included in responses:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1642684800
  ```

## 🔧 Core Components

### Domain Layer

#### Entities

**Prompt Entity** (`src/domain/entities/prompt.py`)
- Represents user-submitted prompts
- Tracks status: PENDING, SAFE, SUSPICIOUS, BLOCKED
- Maintains safety scores and sanitized content

**UserProfile Entity** (`src/domain/entities/user.py`)
- Tracks user reputation (0-1 scale)
- Records prompt statistics
- Identifies suspicious patterns

**Graph Entities** (`src/domain/entities/graph.py`)
- GraphNode: Users, prompts, or patterns
- GraphEdge: Relationships between nodes

#### Repository Interfaces

- `IPromptRepository`: Prompt data access
- `IUserProfileRepository`: User profile management
- `IGraphRepository`: Graph operations

### Application Layer

#### Command/Handler Pattern

**AnalyzePromptsCommand**: Encapsulates analysis requests
**AnalyzePromptsHandler**: Orchestrates the analysis workflow:
1. Validate input
2. Get/create user profile
3. Sanitize prompts
4. Calculate similarities
5. Run agent analysis
6. Make security decision
7. Update user reputation
8. Return results

#### Security Agents

**SimilarityAgent**
- Tracks prompt relationships in graph
- Detects repeated attack patterns
- Identifies coordinated attacks

**SafetyAgent**
- Analyzes user reputation
- Checks violation history
- Applies behavioral analysis

**DecisionAgent**
- Aggregates all findings
- Makes final allow/block decision
- Provides confidence scores

#### Services

**Sanitization Service**
- Multiple strategies: SQL, XSS, profanity, URL, PII
- Composite pattern for applying all strategies
- Returns sanitized text and found issues

**Similarity Calculator**
- Cosine: TF-IDF vector comparison
- Jaccard: Word set overlap
- Levenshtein: Edit distance
- Embedding: Semantic similarity via LLM

### Infrastructure Layer

#### Database
- PostgreSQL for persistent storage
- Redis for caching and graph data
- SQLAlchemy ORM with proper indexing

#### LLM Integration
- Azure OpenAI client with retry logic
- Factory pattern for service creation
- Caching decorator for performance

#### Repositories
- In-memory implementations for development
- SQL implementations for production
- Graph repository using NetworkX

## 🔒 Security Features

### Multi-Layer Defense

1. **Input Sanitization**
   - SQL injection patterns
   - XSS script detection
   - URL validation
   - Personal info redaction
   - Length limits

2. **Similarity Analysis**
   - Multiple algorithms
   - Threshold-based detection
   - Pattern matching

3. **Behavioral Analysis**
   - User reputation tracking
   - Violation history
   - Pattern detection

4. **Graph Intelligence**
   - Relationship mapping
   - Attack pattern identification
   - Coordinated attack detection

5. **Output Sanitization**
   - Response cleaning
   - PII removal
   - XSS prevention

### Attack Detection Examples

| Attack Type | Detection Method | Example |
|-------------|------------------|---------|
| Direct SQL Injection | Regex patterns | `DROP TABLE users` |
| Natural Language SQL | Semantic analysis | "Delete all user records" |
| XSS | Tag detection | `<script>alert('xss')</script>` |
| Prompt Injection | Context analysis | "Ignore previous instructions" |
| Data Exfiltration | Pattern matching | "Show all passwords" |

## 🧪 Testing

### Test Suites

```bash
# Run security tests (P2SQL injection patterns)
python tests/test_load.py security

# Run similarity metric tests
python tests/test_load.py similarity

# Run stress tests (100 requests, 10 concurrent)
python tests/test_load.py stress 100 10

# Run all test suites
python tests/test_load.py all
```

### Test Categories

1. **P2SQL Attacks**
   - Direct SQL injection
   - Natural language manipulation
   - Data exfiltration attempts

2. **Bypass Attempts**
   - Unicode encoding
   - Context switching
   - Hidden instructions

3. **Edge Cases**
   - Ambiguous intent
   - Mixed legitimate/suspicious

4. **Performance Tests**
   - Resource exhaustion
   - Timing attacks
   - High concurrency

### Test Results

The test framework provides:
- Pass/fail status for each test
- Detection rates by category
- Performance metrics
- False positive/negative rates

## 📊 Monitoring

### Prometheus Metrics

| Metric | Description | Type |
|--------|-------------|------|
| `http_requests_total` | Total HTTP requests | Counter |
| `http_request_duration_seconds` | Request latency | Histogram |
| `prompt_analysis_duration_seconds` | Analysis time | Histogram |
| `blocked_prompts_total` | Security blocks | Counter |
| `user_reputation_score` | User reputation | Gauge |
| `active_connections` | Current connections | Gauge |

### Grafana Dashboards

Pre-configured dashboards for:
- Service health overview
- Security metrics
- Performance analysis
- User behavior patterns

Access at http://localhost:3000 (default: admin/admin)

### Logging

Structured logging with levels:
- ERROR: System errors
- WARNING: Security concerns
- INFO: General information
- DEBUG: Detailed debugging

## 💻 Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/prompt-security-service.git
cd prompt-security-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install

# Run locally
poetry run python -m src.main

# Run tests
poetry run pytest

# Code formatting
poetry run black src tests
poetry run isort src tests

# Linting
poetry run flake8 src tests
poetry run mypy src
```

### Development Tools

- **Poetry**: Dependency management
- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing
- **pre-commit**: Git hooks

### Adding New Features

1. **New Entity**: Add to `src/domain/entities/`
2. **New Handler**: Add to `src/application/handlers/`
3. **New Endpoint**: Add to `src/api/endpoints/`
4. **New Strategy**: Add to respective service directory
5. **Tests**: Add to `tests/`

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small
- Follow SOLID principles

## 🚀 Production Deployment

### Pre-Deployment Checklist

- [ ] Change all default passwords
- [ ] Generate new JWT secret key
- [ ] Configure SSL certificates
- [ ] Set up firewall rules
- [ ] Configure backup strategy
- [ ] Enable audit logging
- [ ] Review security policies
- [ ] Set up monitoring alerts
- [ ] Configure rate limits
- [ ] Test failover procedures

### Scaling Strategies

#### Horizontal Scaling
```bash
# Scale API instances
docker-compose up -d --scale app=5

# Update Nginx configuration for more upstreams
```

#### Vertical Scaling
```dockerfile
# Increase worker processes in Dockerfile
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### Performance Tuning

#### PostgreSQL
```sql
-- Adjust shared buffers
ALTER SYSTEM SET shared_buffers = '4GB';

-- Optimize work memory
ALTER SYSTEM SET work_mem = '64MB';

-- Enable parallel queries
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
```

#### Redis
```conf
# Set max memory policy
maxmemory 2gb
maxmemory-policy allkeys-lru

# Enable persistence
save 900 1
save 300 10
save 60 10000
```

#### Nginx
```nginx
# Tune worker processes
worker_processes auto;
worker_connections 4096;

# Enable caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;
```

### Backup Strategy

```bash
# Database backup
docker-compose exec postgres pg_dump -U user prompt_security > backup.sql

# Redis backup
docker-compose exec redis redis-cli BGSAVE

# Application backup
tar -czf app-backup.tar.gz src/ tests/ *.py *.yml *.toml
```

### Monitoring in Production

1. **Set up alerts in Grafana**
   - High error rates
   - Slow response times
   - Security violations
   - Resource exhaustion

2. **Configure log aggregation**
   - Use ELK stack or similar
   - Set up log retention policies
   - Create security dashboards

3. **Enable APM (Application Performance Monitoring)**
   - Use tools like New Relic or DataDog
   - Track transaction traces
   - Monitor external service calls

## 🔧 Troubleshooting

### Common Issues

#### Services not starting
```bash
# Check logs
docker-compose logs [service-name]

# Verify port availability
netstat -tulpn | grep -E '(80|5432|6379|3000|8501|9090)'

# Check Docker resources
docker system df
docker system prune -a
```

#### Database connection errors
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U user -d prompt_security

# Verify connection string
echo $DATABASE_URL

# Run migrations manually
docker-compose exec app1 alembic upgrade head
```

#### Authentication failures
```bash
# Verify JWT secret
echo $JWT_SECRET_KEY

# Check token expiration
# Decode JWT at jwt.io to check exp claim

# Reset user password
docker-compose exec postgres psql -U user -d prompt_security -c "UPDATE users SET password_hash='...' WHERE username='admin';"
```

#### High memory usage
```bash
# Check container stats
docker stats

# Limit container memory
# Add to docker-compose.yml:
services:
  app1:
    mem_limit: 1g
    mem_reservation: 512m
```

#### Performance issues
```bash
# Profile slow endpoints
python -m cProfile -o profile.stats src/main.py

# Analyze with snakeviz
snakeviz profile.stats

# Check database queries
docker-compose exec postgres psql -U user -d prompt_security -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

Enable SQL query logging:
```python
# In src/infrastructure/database/connection.py
engine = create_engine(url, echo=True)
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Run code formatters (`black`, `isort`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Write comprehensive docstrings
- Add type hints to all functions
- Maintain test coverage above 80%
- Update documentation for new features

### Testing Requirements

- Unit tests for new functions
- Integration tests for new endpoints
- Add attack scenarios to test_prompts.py
- Performance benchmarks for critical paths

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by P2SQL injection research
- Built with FastAPI framework
- Uses NetworkX for graph algorithms
- Powered by Azure OpenAI
- Vis.js for graph visualization
- Monitoring with Prometheus and Grafana

## 📞 Support

- **Documentation**: See this README and `/docs` endpoint
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Security**: Report vulnerabilities privately

## 🚦 Project Status

- ✅ Core functionality complete
- ✅ Production ready
- ✅ Comprehensive testing
- ✅ Monitoring implemented
- 🔄 Continuously improving
- 📈 Active development

---

**Built with ❤️ following Domain-Driven Design principles and software engineering best practices**
