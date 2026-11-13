from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

# Import environment_variables to trigger load_environment()
from app.settings import environment_variables  # noqa: F401


class Settings(BaseSettings):
    # App
    app_name: str = "Hotel AI Assistant"
    app_version: str = "1.0.0"
    environment: str = "development"
    testing: bool = Field(default=False, alias="TESTING")
    
    # Hotel Configuration
    hotel_name: str = Field(default="Grand Ocean Hotel", alias="HOTEL_NAME")
    hotel_location: str = Field(default="Lisbon", alias="HOTEL_LOCATION")
    hotel_address: str = Field(default="Rua do Ouro 123, 1100-063 Lisbon, Portugal", alias="HOTEL_ADDRESS")
    hotel_stars: int = Field(default=4, alias="HOTEL_STARS")
    hotel_phone: str = Field(default="+351 (XX) XXXX-XXXX", alias="HOTEL_PHONE")
    hotel_email: str = Field(default="info@grandoceanhotel.com", alias="HOTEL_EMAIL")

    # LLM (Groq)
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = "openai/gpt-oss-120b"
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3

    # Embeddings (Google Gemini)
    embedding_api_key: str = Field(default="", alias="EMBEDDING_API_KEY")
    embedding_model: str = "gemini-embedding-001"
    embedding_timeout_seconds: float = 15.0
    embedding_max_retries: int = 3

    # ChromaDB
    chroma_path: str = "chroma_db"
    chroma_collection: str = "hotel_documents"

    # RAG
    rag_search_limit: int = 5
    rag_distance_threshold: float = 0.9  # Above this = treat as no relevant context (more permissive for hotel queries)

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]
    api_keys: list[str] = Field(default=[], alias="API_KEYS")
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: str = "minute"

    # Redis (for conversation memory)
    redis_url: str = Field(default="", alias="REDIS_URL")

    # PostgreSQL
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="hotel_ai", alias="POSTGRES_DB")
    postgres_user: str = Field(default="hotel_user", alias="POSTGRES_USER")
    postgres_password: str = Field(default="hotel_pass", alias="POSTGRES_PASSWORD")
    postgres_pool_size: int = Field(default=10, alias="POSTGRES_POOL_SIZE")
    postgres_max_overflow: int = Field(default=20, alias="POSTGRES_MAX_OVERFLOW")

    # Conversation Memory
    conversation_ttl_seconds: int = 86400  # 24 hours default
    conversation_max_messages: int = 50  # Max messages per conversation

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # JWT
    jwt_secret: str = Field(default="your-super-secret-jwt-key-change-in-production", alias="JWT_SECRET")

    # Admin User (for initial setup)
    admin_email: str = Field(default="admin@grandoceanhotel.com", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="AdminPass123", alias="ADMIN_PASSWORD")
    admin_name: str = Field(default="Hotel Administrator", alias="ADMIN_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get settings instance. Can be overridden in tests."""
    return Settings()


settings = get_settings()