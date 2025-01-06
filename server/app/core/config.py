from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Rick's Vision"
    APP_VERSION: str = "0.0.1"
    DEBUG: bool = False
    DATABASE_URL: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    model_config = SettingsConfigDict(
        env_file=".env",  # Adjust path if needed
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
