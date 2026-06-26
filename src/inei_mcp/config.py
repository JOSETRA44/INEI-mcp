from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class INEISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cache_ttl: int = Field(default=600, alias="INEI_CACHE_TTL", ge=0)
    timeout: float = Field(default=30.0, alias="INEI_TIMEOUT", gt=0)
    max_retries: int = Field(default=2, alias="INEI_MAX_RETRIES", ge=0, le=5)
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


_settings: INEISettings | None = None


def get_settings() -> INEISettings:
    global _settings
    if _settings is None:
        _settings = INEISettings()
    return _settings
