from pathlib import Path
from dotenv import load_dotenv


def load_environment() -> str:
    """Load environment variables from .env.{environment} file."""
    project_root = Path(__file__).resolve().parents[2]
    
    # Default to development if not set
    environment = "development"
    
    env_file = project_root / f".env.{environment}"
    
    if env_file.exists():
        load_dotenv(env_file, override=True)
    
    return environment


# Load immediately when this module is imported
load_environment()