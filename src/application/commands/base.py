"""Base command classes."""
from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional


class ICommand(ABC):
    """Base interface for commands."""
    
    @abstractmethod
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate command parameters."""
        pass


class ICommandHandler(ABC):
    """Interface for command handlers."""
    
    @abstractmethod
    def handle(self, command: ICommand) -> Any:
        """Handle the command and return result."""
        pass