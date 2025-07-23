"""Core security detection unit tests"""

import pytest
import re

# SQL injection patterns
SQL_PATTERNS = [
    r"DROP\s+TABLE",
    r"DELETE\s+FROM", 
    r"UNION\s+SELECT",
    r"OR\s+\d+=\d+"
]

def detect_sql_injection(text):
    """Detect SQL injection attempts"""
    return any(re.search(p, text.upper()) for p in SQL_PATTERNS)

def detect_xss(text):
    """Detect XSS attempts"""
    xss_indicators = ["<script", "javascript:", "onerror=", "onclick="]
    return any(indicator in text.lower() for indicator in xss_indicators)

def calculate_similarity(text1, text2):
    """Simple Jaccard similarity"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)

class TestSecurity:
    """Security detection tests"""
    
    @pytest.mark.parametrize("malicious_text", [
        "'; DROP TABLE users; --",
        "' OR 1=1 --",
        "UNION SELECT * FROM passwords"
    ])
    def test_sql_injection_detected(self, malicious_text):
        """Test SQL injection detection"""
        assert detect_sql_injection(malicious_text) == True
    
    @pytest.mark.parametrize("safe_text", [
        "Can you drop this from my cart?",
        "Select the best option",
        "I love SQL databases"
    ])
    def test_sql_injection_safe(self, safe_text):
        """Test safe SQL-like text"""
        assert detect_sql_injection(safe_text) == False
    
    @pytest.mark.parametrize("xss_attack", [
        "<script>alert(1)</script>",
        "<img onerror='alert(1)'>",
        "<a href='javascript:void(0)'>"
    ])
    def test_xss_detected(self, xss_attack):
        """Test XSS detection"""
        assert detect_xss(xss_attack) == True
    
    @pytest.mark.parametrize("text1,text2,expected", [
        ("hello world", "hello world", 1.0),
        ("hello world", "hello", 0.5),
        ("cat dog", "fish bird", 0.0),
        ("the quick fox", "quick fox jumps", 0.5)
    ])
    def test_similarity_calculation(self, text1, text2, expected):
        """Test similarity scores"""
        score = calculate_similarity(text1, text2)
        assert abs(score - expected) < 0.01
