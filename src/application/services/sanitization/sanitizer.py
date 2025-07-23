"""Composite sanitizer implementation."""
from typing import List, Tuple

from src.application.services.sanitization.strategies import ISanitizationStrategy


class ISanitizer:
    """Interface for sanitizers."""
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Sanitize text and return issues."""
        raise NotImplementedError


class CompositeSanitizer(ISanitizer):
    """Composite sanitizer that applies multiple strategies."""
    
    def __init__(self, strategies: List[ISanitizationStrategy]):
        """Initialize with list of strategies."""
        self._strategies = strategies
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Apply all sanitization strategies."""
        all_issues = []
        sanitized = text
        
        for strategy in self._strategies:
            sanitized, issues = strategy.sanitize(sanitized)
            all_issues.extend(issues)
        
        return sanitized, all_issues