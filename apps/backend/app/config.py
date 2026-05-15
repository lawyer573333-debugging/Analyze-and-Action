from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Insight-to-Action Engine"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin_password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "insight_to_action"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    REDIS_URL: str = "redis://localhost:6379"
    
    SECRET_KEY: str = "secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
