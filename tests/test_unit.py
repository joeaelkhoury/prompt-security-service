# tests/test_unit.py
"""Unit tests for core functionality."""

import pytest
from src.domain.entities.prompt import Prompt, PromptStatus
from src.domain.entities.user import UserProfile
from src.application.services.sanitization.strategies import SQLInjectionSanitizer, XSSSanitizer
from src.application.services.similarity.strategies import CosineSimilarityStrategy, JaccardSimilarityStrategy


class TestDomainModels:
    def test_prompt_creation(self):
        prompt = Prompt(user_id="user123", content="What is AI?")
        assert prompt.user_id == "user123"
        assert prompt.status == PromptStatus.PENDING
    
    def test_user_profile_reputation(self):
        profile = UserProfile(user_id="user123")
        profile.update_reputation(is_safe=False)
        assert profile.reputation_score < 1.0
        assert profile.blocked_prompts == 1


class TestSanitizers:
    def test_sql_injection_detection(self):
        sanitizer = SQLInjectionSanitizer()
        text = "'; DROP TABLE users; --"
        sanitized, issues = sanitizer.sanitize(text)
        assert "[REMOVED]" in sanitized
        assert len(issues) > 0
    
    def test_xss_detection(self):
        sanitizer = XSSSanitizer()
        text = '<script>alert("XSS")</script>'
        sanitized, issues = sanitizer.sanitize(text)
        assert "&lt;script&gt;" in sanitized
        assert "Script tags detected" in issues[0]


class TestSimilarity:
    def test_cosine_similarity(self):
        strategy = CosineSimilarityStrategy()
        score = strategy.calculate("hello world", "hello world")
        # Use pytest.approx for floating-point comparison
        assert score == pytest.approx(1.0, rel=1e-9)
    
    def test_jaccard_similarity(self):
        strategy = JaccardSimilarityStrategy()
        score = strategy.calculate("the quick fox", "the fox")
        assert 0 < score < 1