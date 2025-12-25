from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "WEB DIABETES API"
    ENV: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str | None = None
    ADMIN_PASSWORD_HASH: str | None = None
    CORS_ORIGINS: str | None = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


settings = Settings()
