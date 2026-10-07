from pathlib import Path

from dotenv import load_dotenv


def load_environment():
    project_root = Path(__file__).resolve().parents[2]

    environment = "development"

    env_file = project_root / f".env.{environment}"

    load_dotenv(env_file, override=True)

    return environment