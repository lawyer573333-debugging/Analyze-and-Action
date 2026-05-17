from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Insight-to-Action Engine"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Database - from environment, no defaults
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security - must be set in environment
    SECRET_KEY: str  # Must be 32+ chars, use: python -c "import secrets; print(secrets.token_urlsafe(32))"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI/LLM APIs
    GEMINI_API_KEY_PRIMARY: str = None
    GEMINI_API_KEY_SECONDARY: str = None

    # GCP / Vertex AI (Optional)
    VERTEX_LOCATION: str = "us-central1"
    GCP_PROJECT_ID: str = None
    VERTEX_AGENT_ID: str = None
    GCP_KEY_PATH: str = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        # Validate that required fields are set
        if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD or not self.POSTGRES_DB:
            raise ValueError(
                "Missing required environment variables: "
                "POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB must be set in .env file"
            )
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set in .env file. "
                "Generate one: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if self.ENVIRONMENT not in ["development", "staging", "production"]:
            raise ValueError("ENVIRONMENT must be one of: development, staging, production")

settings = Settings()
