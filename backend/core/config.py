"""
Application Configuration Management

Loads and validates all environment variables using Pydantic Settings.
Provides type-safe access to configuration throughout the application.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have sensible defaults for development.
    Production deployments should override via .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # APPLICATION SETTINGS
    # =========================================================================
    APP_NAME: str = "Wealth Coach AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # =========================================================================
    # LLM CONFIGURATION
    # =========================================================================
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_TIMEOUT: int = 30

    ENABLE_LOCAL_FALLBACK: bool = True
    LOCAL_MODEL_PATH: str = "./models/llama-2-7b-chat"

    COHERE_API_KEY: Optional[str] = None
    COHERE_MODEL: str = "command-light"

    MAX_TOKENS_PER_REQUEST: int = 500
    MAX_REQUESTS_PER_USER_PER_DAY: int = 100
    ENABLE_STREAMING: bool = True

    # =========================================================================
    # VECTOR DATABASE (pgvector - Supabase)
    # =========================================================================
    # Vector database now uses pgvector extension in PostgreSQL (see DATABASE_URL)

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    TOKENIZERS_PARALLELISM: str = "false"  # Disable to avoid fork warnings

    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    RAG_MAX_CONTEXT_LENGTH: int = 2000

    # =========================================================================
    # CACHING (Redis)
    # =========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 50

    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    QUERY_CACHE_TTL: int = 7200
    EMBEDDING_CACHE_TTL: int = 86400
    CACHE_HIT_RATE_TARGET: float = 0.9

    # =========================================================================
    # DATABASE (PostgreSQL)
    # =========================================================================
    DATABASE_URL: str = "postgresql://localhost/wealth_coach"
    DATABASE_ECHO: bool = False  # Set to True to see SQL queries in logs
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # =========================================================================
    # AUTHENTICATION & SECURITY
    # =========================================================================
    JWT_SECRET_KEY: str = Field(
        default="INSECURE-DEV-KEY-CHANGE-IN-PRODUCTION",
        description="Secret key for JWT token signing",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PASSWORD_MIN_LENGTH: int = 8
    BCRYPT_ROUNDS: int = 12

    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:19006", "http://localhost:5173", "null"]
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    API_KEY_HEADER: str = "X-API-Key"
    VALID_API_KEYS: List[str] = Field(default=["dev-key-12345"])

    # =========================================================================
    # RATE LIMITING
    # =========================================================================
    RATE_LIMIT_ENABLED: bool = False  # Temporarily disabled for CORS testing
    RATE_LIMIT_PER_MINUTE: int = 20
    RATE_LIMIT_PER_HOUR: int = 200
    RATE_LIMIT_PER_DAY: int = 1000

    CHAT_RATE_LIMIT_PER_MINUTE: int = 10
    SEARCH_RATE_LIMIT_PER_MINUTE: int = 30

    # =========================================================================
    # WEBSOCKET CONFIGURATION
    # =========================================================================
    WS_ENABLED: bool = True
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS_PER_USER: int = 3
    WS_MESSAGE_MAX_SIZE: int = 65536

    # =========================================================================
    # MONITORING & LOGGING
    # =========================================================================
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    LOG_FORMAT: str = "json"
    LOG_FILE: str = "./logs/wealth_coach.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"

    # =========================================================================
    # FINANCIAL DATA SOURCES
    # =========================================================================
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    IEX_CLOUD_API_KEY: Optional[str] = None
    ENABLE_YAHOO_FINANCE: bool = True

    # =========================================================================
    # CONTENT & KNOWLEDGE BASE
    # =========================================================================
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    AUTO_RELOAD_KNOWLEDGE: bool = False
    SUPPORTED_FILE_TYPES: List[str] = Field(default=["pdf", "md", "txt", "docx"])

    MAX_DOCUMENT_SIZE_MB: int = 10
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    ENABLE_USER_REGISTRATION: bool = True
    ENABLE_CONVERSATION_HISTORY: bool = True
    ENABLE_PERSONALIZATION: bool = True
    ENABLE_ANALYTICS: bool = True

    # =========================================================================
    # API DOCUMENTATION
    # =========================================================================
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_REDOC: bool = True

    # =========================================================================
    # COMPLIANCE & PRIVACY
    # =========================================================================
    CONVERSATION_RETENTION_DAYS: int = 90
    USER_DATA_RETENTION_DAYS: int = 365
    ANONYMIZE_LOGS: bool = True
    STORE_IP_ADDRESSES: bool = False
    ENABLE_GDPR_COMPLIANCE: bool = True

    FINANCIAL_DISCLAIMER: str = (
        "This AI assistant provides educational information only and is not "
        "a substitute for professional financial advice."
    )

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("VALID_API_KEYS", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        """Parse API keys from JSON string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("SUPPORTED_FILE_TYPES", mode="before")
    @classmethod
    def parse_file_types(cls, v):
        """Parse file types from JSON string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v, info):
        """Warn if using default JWT secret in production."""
        if info.data.get("ENVIRONMENT") == "production" and v == "INSECURE-DEV-KEY-CHANGE-IN-PRODUCTION":
            raise ValueError(
                "JWT_SECRET_KEY must be changed from default value in production!"
            )
        return v

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v, info):
        """Warn if OpenAI key is missing and fallback is disabled."""
        if not v and not info.data.get("ENABLE_LOCAL_FALLBACK", True):
            raise ValueError(
                "OPENAI_API_KEY is required when ENABLE_LOCAL_FALLBACK is False"
            )
        return v if v else ""  # Return empty string instead of None

    # =========================================================================
    # COMPUTED PROPERTIES
    # =========================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def redis_config(self) -> dict:
        """Get Redis connection configuration."""
        return {
            "url": self.REDIS_URL,
            "password": self.REDIS_PASSWORD,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "decode_responses": True,
        }

    @property
    def openai_config(self) -> dict:
        """Get OpenAI client configuration."""
        return {
            "api_key": self.OPENAI_API_KEY,
            "model": self.OPENAI_MODEL,
            "max_tokens": self.OPENAI_MAX_TOKENS,
            "temperature": self.OPENAI_TEMPERATURE,
            "timeout": self.OPENAI_TIMEOUT,
        }


# Global settings instance
settings = Settings()


# Development checks
if settings.DEBUG:
    print(f"⚠️  Running in DEBUG mode")
    print(f"📝 Log level: {settings.LOG_LEVEL}")
    print(f"🔌 Server: {settings.HOST}:{settings.PORT}")
    print(f"💾 Redis: {settings.REDIS_URL}")
    print(f"🗄️  Vector DB: pgvector (PostgreSQL)")
    print(f"🤖 LLM Model: {settings.OPENAI_MODEL}")
    print(f"💰 Max tokens per request: {settings.MAX_TOKENS_PER_REQUEST}")
