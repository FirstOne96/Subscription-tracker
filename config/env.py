from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.development.local",
        extra="ignore",
        case_sensitive=True
    )

    PORT: int = 8000
    SERVER_URL: str = "http://localhost:8000"
    NODE_ENV: str = "development"

    MONGODB_URI: str
    JWT_SECRET: str
    JWT_EXPIRES_IN: str = "1d"

    REDIS_URL: str = "redis://localhost:6379/0"

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False


settings = Settings()
