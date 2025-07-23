"""Sanitization strategies."""
import re
import html
from typing import Tuple, List
from urllib.parse import urlparse

from src.core.constants import PatternType


class ISanitizationStrategy:
    """Interface for sanitization strategies."""
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Sanitize text and return sanitized version with issues."""
        raise NotImplementedError


class SQLInjectionSanitizer(ISanitizationStrategy):
    """Sanitizer for SQL injection attempts."""
    
    SQL_PATTERNS = [
        r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b',
        r'(--|#|\/\*|\*\/)',
        r'(\' or \'|\' or 1=1|\" or \"|\" or 1=1)',
        r'(xp_cmdshell|sp_executesql)',
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize SQL injection patterns."""
        issues = []
        sanitized = text
        
        for pattern in self.SQL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(f"{PatternType.SQL_INJECTION.value}: {matches[0]}")
                sanitized = re.sub(pattern, '[REMOVED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized, issues


class XSSSanitizer(ISanitizationStrategy):
    """Sanitizer for XSS attempts."""
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize XSS patterns."""
        issues = []
        
        # Check for script tags
        if re.search(r'<script.*?>.*?</script>', text, re.IGNORECASE | re.DOTALL):
            issues.append(f"{PatternType.XSS_ATTACK.value}: Script tags detected")
        
        # Check for event handlers
        if re.search(r'on\w+\s*=', text, re.IGNORECASE):
            issues.append(f"{PatternType.XSS_ATTACK.value}: Event handlers detected")
        
        # HTML escape the text
        sanitized = html.escape(text)
        
        return sanitized, issues


class ProfanitySanitizer(ISanitizationStrategy):
    """Sanitizer for profanity and inappropriate content."""
    
    PROFANITY_LIST = [
        "badword1", "badword2", "inappropriate"
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize profanity."""
        issues = []
        sanitized = text
        
        for word in self.PROFANITY_LIST:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                issues.append(f"{PatternType.PROFANITY.value}: {word}")
                sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized, issues


class LengthLimitSanitizer(ISanitizationStrategy):
    """Sanitizer for length limits."""
    
    def __init__(self, max_length: int = 2000):
        """Initialize with max length."""
        self.max_length = max_length
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Check and enforce length limits."""
        issues = []
        
        if len(text) > self.max_length:
            issues.append(
                f"{PatternType.EXCESSIVE_LENGTH.value}: Exceeds {self.max_length} chars"
            )
            return text[:self.max_length], issues
        
        return text, issues


class URLSanitizer(ISanitizationStrategy):
    """Sanitizer for suspicious URLs."""
    
    SUSPICIOUS_DOMAINS = [
        "malicious.com", "phishing.net", "spam.org"
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize suspicious URLs."""
        issues = []
        sanitized = text
        
        # Find all URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                if any(suspicious in domain for suspicious in self.SUSPICIOUS_DOMAINS):
                    issues.append(f"{PatternType.SUSPICIOUS_URL.value}: {url}")
                    sanitized = sanitized.replace(url, '[URL_REMOVED]')
            except:
                pass
        
        return sanitized, issues


class PersonalInfoSanitizer(ISanitizationStrategy):
    """Sanitizer for personal information."""
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize personal information."""
        issues = []
        sanitized = text
        
        # Phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, text):
            issues.append("Personal info: Phone number detected")
            sanitized = re.sub(phone_pattern, '[PHONE_REMOVED]', sanitized)
        
        # SSN
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        if re.search(ssn_pattern, text):
            issues.append("Personal info: SSN pattern detected")
            sanitized = re.sub(ssn_pattern, '[SSN_REMOVED]', sanitized)
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            issues.append("Personal info: Email address detected")
            sanitized = re.sub(email_pattern, '[EMAIL_REMOVED]', sanitized)
        
        return sanitized, issues