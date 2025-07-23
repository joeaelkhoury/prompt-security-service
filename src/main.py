"""Main entry point for the application."""
import uvicorn

from src.core.config import Settings
from src.api.app import create_app


def main():
    """Run the application."""
    settings = Settings.from_env()
    app = create_app(settings)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()