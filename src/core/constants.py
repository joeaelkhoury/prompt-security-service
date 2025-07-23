"""Application constants."""
from enum import Enum


class AgentRecommendation(Enum):
    """Recommendations from security agents."""
    ALLOW = "allow"
    INVESTIGATE = "investigate"
    BLOCK = "block"
    REVIEW = "review"


class PatternType(Enum):
    """Types of security patterns detected."""
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PROFANITY = "profanity"
    EXCESSIVE_LENGTH = "excessive_length"
    SUSPICIOUS_URL = "suspicious_url"
    PERSONAL_INFO = "personal_info"
    DATA_EXFILTRATION = "data_exfiltration"
    PROMPT_INJECTION = "prompt_injection"
    EXCESSIVE_SIMILAR_PROMPTS = "excessive_similar_prompts"
    RAPID_FIRE_QUERIES = "rapid_fire_queries"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


class PromptStatus(Enum):
    """Status of prompt processing."""
    PENDING = "pending"
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"
