"""Application constants."""
from enum import Enum


class PatternType(Enum):
    """Types of suspicious patterns."""
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PROFANITY = "profanity"
    EXCESSIVE_LENGTH = "excessive_length"
    SUSPICIOUS_URL = "suspicious_url"
    REPEATED_VIOLATIONS = "repeated_violations"
    EXCESSIVE_SIMILAR_PROMPTS = "excessive_similar_prompts"


class AgentRecommendation(Enum):
    """Agent recommendation types."""
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"
    INVESTIGATE = "investigate"