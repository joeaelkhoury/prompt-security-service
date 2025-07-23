"""
Security sanitization strategies for prompt analysis.
"""
import re
import html
from typing import Tuple, List
from urllib.parse import urlparse

from src.core.constants import PatternType


class ISanitizationStrategy:
    """Base interface for sanitization strategies."""
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """
        Analyze text for security issues and optionally sanitize it.
        
        Args:
            text: The input text to analyze
            
        Returns:
            Tuple of (sanitized_text, list_of_issues_found)
        """
        raise NotImplementedError


class SQLInjectionSanitizer(ISanitizationStrategy):
    """Detects SQL injection attempts in both direct SQL and natural language."""
    
    # Direct SQL injection patterns
    SQL_SYNTAX_PATTERNS = [
        # SQL statements with suspicious structure
        r"(?i)(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+(?:.*?\s+)?(?:FROM|INTO|TABLE|DATABASE|WHERE)\s+[\w`\"']+",
        # SQL comments
        r'(?:--|#|\/\*.*?\*\/)\s*$',
        # Classic injection patterns
        r"(?i)[\'\"]?\s*OR\s*[\'\"]?1[\'\"]?\s*=\s*[\'\"]?1",
        r"(?i)[\'\"]?\s*OR\s+[\'\"]?[^\s]+[\'\"]?\s*=\s*[\'\"]?[^\s]+",
        # Union-based attacks
        r"(?i)UNION\s+(?:ALL\s+)?SELECT",
        # Stacked queries
        r";\s*(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)",
        # Dangerous functions
        r"(?i)(?:xp_cmdshell|sp_executesql|exec\s*\(|execute\s*\()",
        # Hex encoding
        r"(?i)(?:0x[0-9a-f]+|char\s*\([0-9]+\))",
        # Time-based blind SQL
        r"(?i)(?:sleep|waitfor\s+delay|benchmark|pg_sleep)\s*\(",
    ]
    
    # Natural language SQL command patterns
    NATURAL_LANGUAGE_PATTERNS = [
        # Database modification commands in natural language
        r'(?i)(?:change|update|modify|set)\s+(?:the\s+)?(?:phone|email|password|role|permission|name|address)',
        r'(?i)(?:make|set)\s+(?:me|user|someone|them)\s+(?:an?\s+)?(?:admin|superadmin|root|moderator)',
        r'(?i)modify\s+(?:the\s+)?database',
        r'(?i)set\s+(?:all\s+)?(?:user\s+)?passwords?\s+to',
        r'(?i)update\s+(?:their|his|her|my|user)\s+(?:role|permission|access|privilege)',
        r'(?i)give\s+(?:me|user|them|someone)\s+(?:admin|super|root|elevated)\s+(?:access|privileges?|permissions?)',
        r'(?i)delete\s+(?:all\s+)?(?:user|account|record)s?\s+(?:from|in)',
        r'(?i)remove\s+(?:all\s+)?(?:user|account|customer)\s+(?:data|records?|information)',
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect SQL injection attempts in various forms."""
        issues = []
        sanitized = text
        
        # Check for direct SQL patterns
        for pattern in self.SQL_SYNTAX_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"{PatternType.SQL_INJECTION.value}: SQL syntax pattern detected")
                # Only sanitize if it's actual SQL, not just keywords in sentences
                if self._is_likely_sql(text):
                    sanitized = re.sub(pattern, '[REMOVED]', sanitized, flags=re.IGNORECASE)
                break
        
        # Check for natural language SQL commands
        for pattern in self.NATURAL_LANGUAGE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"{PatternType.SQL_INJECTION.value}: Natural language database command detected")
                break
        
        return sanitized, issues
    
    def _is_likely_sql(self, text: str) -> bool:
        """Determine if text contains actual SQL syntax vs. just keywords."""
        sql_indicators = [
            r';\s*$',  # Ends with semicolon
            r'--\s',   # SQL comment
            r'/\*',    # Multi-line comment
            r'\bFROM\s+\w+\s+WHERE\b',  # SQL clause structure
            r'\bVALUES\s*\(',  # INSERT VALUES
            r'\bSET\s+\w+\s*=',  # UPDATE SET
        ]
        
        for indicator in sql_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                return True
        return False


class XSSSanitizer(ISanitizationStrategy):
    """Detects and prevents Cross-Site Scripting (XSS) attacks."""
    
    XSS_PATTERNS = [
        # Script tags
        r'<script[^>]*>.*?</script>',
        # JavaScript event handlers
        r'on\w+\s*=\s*["\'].*?["\']',
        # JavaScript protocol
        r'javascript\s*:',
        # Other dangerous tags
        r'<(?:iframe|object|embed|link|style|base|form)[^>]*>',
        # SVG-based XSS
        r'<svg[^>]*onload[^>]*>',
        # Data URLs with scripts
        r'data:[^,]*script',
        # Expression/eval patterns
        r'(?:eval|expression|Function)\s*\(',
        # Import/document.write
        r'(?:import|document\.write)\s*\(',
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize XSS patterns."""
        issues = []
        
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                issues.append(f"{PatternType.XSS_ATTACK.value}: Potential XSS pattern detected")
                break
        
        # HTML escape if XSS patterns found
        if issues and re.search(r'<[^>]+>', text):
            sanitized = html.escape(text)
        else:
            sanitized = text
        
        return sanitized, issues


class DataExfiltrationSanitizer(ISanitizationStrategy):
    """Detects attempts to extract sensitive data."""
    
    # Sensitive data types
    SENSITIVE_DATA_TERMS = [
        'password', 'pwd', 'passwd', 'credential', 'secret', 'token', 'api_key',
        'ssn', 'social_security', 'social security', 'credit_card', 'credit card',
        'bank_account', 'bank account', 'private_key', 'private key'
    ]
    
    # Data extraction verbs
    EXTRACTION_VERBS = [
        'dump', 'export', 'extract', 'show', 'list', 'display', 'give', 'provide',
        'send', 'email', 'download', 'copy', 'transfer', 'leak', 'steal'
    ]
    
    # Bulk data indicators
    BULK_INDICATORS = [
        'all', 'entire', 'complete', 'every', 'whole', 'full', '*'
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect data exfiltration attempts."""
        issues = []
        text_lower = text.lower()
        
        # Pattern 1: Direct requests for sensitive data
        if self._contains_sensitive_data_request(text_lower):
            issues.append(f"{PatternType.DATA_EXFILTRATION.value}: Sensitive data request detected")
        
        # Pattern 2: Bulk data extraction
        if self._contains_bulk_extraction(text_lower):
            issues.append(f"{PatternType.DATA_EXFILTRATION.value}: Bulk data extraction attempt")
        
        # Pattern 3: Database structure exploration
        if 'information_schema' in text_lower or 'show tables' in text_lower:
            issues.append(f"{PatternType.DATA_EXFILTRATION.value}: Database structure exploration")
        
        # Pattern 4: Specific SQL data extraction
        if self._contains_sql_extraction(text_lower):
            issues.append(f"{PatternType.DATA_EXFILTRATION.value}: SQL data extraction pattern")
        
        return text, issues
    
    def _contains_sensitive_data_request(self, text: str) -> bool:
        """Check if text requests sensitive data."""
        has_extraction_verb = any(verb in text for verb in self.EXTRACTION_VERBS)
        has_sensitive_term = any(term in text for term in self.SENSITIVE_DATA_TERMS)
        return has_extraction_verb and has_sensitive_term
    
    def _contains_bulk_extraction(self, text: str) -> bool:
        """Check for bulk data extraction attempts."""
        has_bulk = any(bulk in text for bulk in self.BULK_INDICATORS)
        has_data_terms = any(term in text for term in ['user', 'customer', 'account', 'record', 'data', 'database', 'table'])
        has_extraction = any(verb in text for verb in self.EXTRACTION_VERBS)
        return has_bulk and has_data_terms and has_extraction
    
    def _contains_sql_extraction(self, text: str) -> bool:
        """Check for SQL-based data extraction."""
        if 'select' in text:
            return any(term in text for term in self.SENSITIVE_DATA_TERMS)
        return False


class PromptInjectionSanitizer(ISanitizationStrategy):
    """Detects prompt injection and jailbreak attempts."""
    
    INJECTION_PATTERNS = [
        # Instruction override attempts
        r'(?i)(?:ignore|forget|disregard)\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions?|commands?|prompts?)',
        r'(?i)(?:ignore|forget|disregard)\s+(?:the\s+)?(?:rules?|restrictions?|guidelines?|policies)',
        # Role/mode switching
        r'(?i)you\s+are\s+now\s+(?:in\s+)?(?:admin|debug|root|system|developer|god)\s+mode',
        r'(?i)(?:enter|enable|activate)\s+(?:admin|debug|maintenance|developer)\s+mode',
        r'(?i)i\s+am\s+(?:now\s+)?(?:the\s+)?(?:admin|administrator|root|system|owner)',
        r'(?i)switch\s+to\s+(?:admin|root|system|unrestricted)\s+(?:mode|context|role)',
        # System prompt manipulation
        r'(?i)(?:system|admin)\s*:\s*(?:you|ignore|allow)',
        r'(?i)\[\[?(?:system|admin|root)\]\]?',
        r'(?i)\{\{(?:system|admin|root)\}\}',
        # Hidden instructions
        r'<!--[\s\S]*?(?:ignore|admin|system|execute)[\s\S]*?-->',
        r'/\*[\s\S]*?(?:ignore|admin|system|execute)[\s\S]*?\*/',
        # Context confusion
        r'(?i)pretend\s+(?:you\s+are|to\s+be|that)',
        r'(?i)act\s+(?:as\s+if|like|as)\s+(?:you|an?)',
        # Instruction insertion
        r'(?i)new\s+(?:rule|instruction|command)\s*:',
        r'(?i)from\s+now\s+on\s*[,:]',
    ]
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect prompt injection attempts."""
        issues = []
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                issues.append(f"{PatternType.PROMPT_INJECTION.value}: Prompt injection attempt detected")
                break
        
        # Don't modify the text, just flag it
        return text, issues


class PersonalInfoSanitizer(ISanitizationStrategy):
    """Detects and redacts personal identifiable information (PII)."""
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and redact personal information."""
        issues = []
        sanitized = text
        
        # Phone numbers (US format)
        phone_patterns = [
            r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
        ]
        
        for pattern in phone_patterns:
            if re.search(pattern, text):
                issues.append("Personal info: Phone number detected")
                sanitized = re.sub(pattern, '[PHONE_REMOVED]', sanitized)
                break
        
        # Social Security Numbers
        ssn_pattern = r'\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b'
        if re.search(ssn_pattern, text):
            # Only flag if context suggests SSN
            if re.search(r'(?i)(?:ssn|social.{0,10}security|tax.{0,10}id)', text):
                issues.append("Personal info: SSN pattern detected")
                sanitized = re.sub(ssn_pattern, '[SSN_REMOVED]', sanitized)
        
        # Email addresses (but not system/example emails)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        for email in emails:
            if not any(x in email.lower() for x in ['example.com', 'test.com', 'localhost', 'admin@', 'noreply@']):
                issues.append("Personal info: Email address detected")
                sanitized = sanitized.replace(email, '[EMAIL_REMOVED]')
        
        # Credit card numbers (basic pattern)
        cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        if re.search(cc_pattern, text):
            issues.append("Personal info: Credit card pattern detected")
            sanitized = re.sub(cc_pattern, '[CC_REMOVED]', sanitized)
        
        return sanitized, issues


class URLSanitizer(ISanitizationStrategy):
    """Detects and validates URLs for security threats."""
    
    # Known malicious domains and patterns
    SUSPICIOUS_DOMAINS = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'is.gd', 't.co',  # URL shorteners
        'grabify.link', 'iplogger.org', 'iplogger.com', '2no.co', 'blasze.com',  # IP loggers
    ]
    
    # Suspicious TLDs often used in phishing
    SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.click', '.download', '.review']
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize suspicious URLs."""
        issues = []
        sanitized = text
        
        # Find all URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            if self._is_suspicious_url(url):
                issues.append(f"{PatternType.SUSPICIOUS_URL.value}: Suspicious URL detected")
                sanitized = sanitized.replace(url, '[URL_REMOVED]')
        
        # Check for IP addresses (potential phishing)
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        if re.search(ip_pattern, text):
            issues.append(f"{PatternType.SUSPICIOUS_URL.value}: Direct IP address detected")
        
        return sanitized, issues
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL is suspicious."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check against suspicious domains
            if any(suspicious in domain for suspicious in self.SUSPICIOUS_DOMAINS):
                return True
            
            # Check suspicious TLDs
            if any(domain.endswith(tld) for tld in self.SUSPICIOUS_TLDS):
                return True
            
            # Check for homograph attacks (unicode in domain)
            if not all(ord(char) < 128 for char in domain):
                return True
            
            return False
        except:
            # Malformed URL is suspicious
            return True


class ProfanitySanitizer(ISanitizationStrategy):
    """Detects and filters inappropriate language."""
    
    # loaded from a configuration file
    PROFANITY_LIST = []
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Detect and sanitize profanity."""
        issues = []
        sanitized = text
        
        for word in self.PROFANITY_LIST:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                issues.append(f"{PatternType.PROFANITY.value}: Inappropriate content")
                sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return sanitized, issues


class LengthLimitSanitizer(ISanitizationStrategy):
    """Enforces text length limits to prevent resource exhaustion."""
    
    def __init__(self, max_length: int = 5000):
        """Initialize with maximum allowed length."""
        self.max_length = max_length
    
    def sanitize(self, text: str) -> Tuple[str, List[str]]:
        """Check and enforce length limits."""
        issues = []
        
        if len(text) > self.max_length:
            issues.append(
                f"{PatternType.EXCESSIVE_LENGTH.value}: Text exceeds {self.max_length} characters"
            )
            return text[:self.max_length] + "...[TRUNCATED]", issues
        
        return text, issues
