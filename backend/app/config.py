from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = "postgresql+psycopg://forr:forr_dev@localhost:5432/forr_db"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = True

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()
