"""Custom exceptions for the application."""


class DomainException(Exception):
    """Base exception for domain logic errors."""
    pass


class ApplicationException(Exception):
    """Base exception for application logic errors."""
    pass


class InfrastructureException(Exception):
    """Base exception for infrastructure errors."""
    pass


class ConfigurationException(Exception):
    """Exception for configuration errors."""
    pass