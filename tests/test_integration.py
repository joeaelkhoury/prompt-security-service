"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
from dotenv import load_dotenv

load_dotenv()

# Import after loading env
from src.api.app import create_app
from src.core.config import Settings


@pytest.fixture
def test_client():
    settings = Settings.from_env()
    app = create_app(settings)
    return TestClient(app)


class TestAPI:
    def test_health(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch('src.infrastructure.llm.azure_client.AzureOpenAI')
    def test_analyze_prompts(self, mock_azure, test_client):
        # Mock Azure OpenAI responses
        mock_azure.return_value.chat.completions.create.return_value.choices = [
            type('obj', (object,), {'message': type('msg', (object,), {'content': 'Test response'})})()
        ]
        mock_azure.return_value.embeddings.create.return_value.data = [
            type('obj', (object,), {'embedding': [0.1] * 1536})()
        ]
        
        response = test_client.post("/analyze", json={
            "user_id": "test_user",
            "prompt1": "What is machine learning?",
            "prompt2": "Explain ML",
            "similarity_threshold": 0.5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "similarity_scores" in data
    
    def test_analyze_with_sql_injection(self, test_client):
        response = test_client.post("/analyze", json={
            "user_id": "malicious",
            "prompt1": "'; DROP TABLE users; --",
            "prompt2": "SELECT * FROM passwords"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["llm_response"] is None 