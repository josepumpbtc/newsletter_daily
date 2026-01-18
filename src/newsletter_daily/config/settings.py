"""Æ-Mn - / .env ¯ƒØÏ"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    # src/newsletter_daily/config/settings.py -> parents[3] = yî9
    return Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    timezone: str = Field(default="Asia/Hong_Kong", description="¦ö:")
    newsletter_hour: int = Field(default=10, ge=0, le=23)
    newsletter_minute: int = Field(default=0, ge=0, le=59)

    theinformation_email: Optional[str] = Field(default=None, env="THEINFORMATION_EMAIL")
    theinformation_password: Optional[str] = Field(default=None, env="THEINFORMATION_PASSWORD")

    telegram_bot_token: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")

    web_host: str = Field(default="0.0.0.0")
    web_port: int = Field(default=8080, ge=1, le=65535)

    project_root: Path = Field(default_factory=_project_root)
    sources_config_path: Path = Field(
        default_factory=lambda: _project_root() / "config" / "sources.yaml"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
