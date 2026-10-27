"""Global configuration and application parameters loaded via Pydantic from .env."""

from pathlib import Path
from typing import Dict, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving .env location
BASE_DIR: Path = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Application settings schema validated with Pydantic and loaded from .env."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Embedding and similarity settings
    EMBEDDING_MODEL_NAME: str = Field(
        default="BAAI/bge-m3",
        description="HuggingFace model ID for dense semantic embeddings",
    )
    SIMILARITY_HIGH_THRESHOLD: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Threshold score for High Similarity classification",
    )
    SIMILARITY_MODERATE_THRESHOLD: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Threshold score for Moderate Similarity classification",
    )

    # HTTP and scraping configuration
    USER_AGENT: str = Field(
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        description="Standard browser User-Agent header string",
    )
    REQUEST_TIMEOUT: float = Field(
        default=12.0,
        gt=0.0,
        description="HTTP request timeout in seconds",
    )
    MIN_POST_LENGTH: int = Field(
        default=35,
        ge=1,
        description="Minimum character length threshold to discard empty or media-only captions",
    )

    # Platform endpoints and default channels
    EITAA_BASE_URL: str = Field(
        default="https://eitaa.com",
        description="Base web preview URL for Eitaa",
    )
    BALE_BASE_URL: str = Field(
        default="https://ble.ir",
        description="Base web preview URL for Bale",
    )

    DEFAULT_EITAA_CHANNEL: str = Field(
        default="farsna",
        description="Default public Eitaa channel identifier",
    )
    DEFAULT_BALE_CHANNEL: str = Field(
        default="iribnews",
        description="Default public Bale channel identifier",
    )

    # Channel presets for quick testing in UI
    POPULAR_CHANNELS: Dict[str, List[str]] = Field(
        default={
            "Eitaa": ["farsna", "tasnimnews", "iribnews", "akharinkhabar", "mehrnews", "isna", "irnanews"],
            "Bale": ["iribnews", "farsna", "tasnimnews", "akharinkhabar", "mehrnews", "isna", "irnanews"],
        },
        description="Popular Iranian news channel handles for quick selection",
    )


# Instantiate singleton settings instance
settings = Settings()

# Friendly Persian names for popular news agencies
NEWS_AGENCIES: Dict[str, str] = {
    "farsna": "خبرگزاری فارس",
    "tasnimnews": "خبرگزاری تسنیم",
    "iribnews": "خبرگزاری صدا و سیما",
    "akharinkhabar": "آخرین خبر",
    "mehrnews": "خبرگزاری مهر",
    "isna": "خبرگزاری ایسنا",
    "irnanews": "خبرگزاری ایرنا",
}


def get_channel_display_name(channel_id: str) -> str:
    """Return friendly Persian news agency name or formatted handle."""
    clean = channel_id.strip().lstrip("@")
    return NEWS_AGENCIES.get(clean, f"کانال @{clean}")


# Re-export settings attributes at module level for seamless backwards compatibility
EMBEDDING_MODEL_NAME: str = settings.EMBEDDING_MODEL_NAME
SIMILARITY_HIGH_THRESHOLD: float = settings.SIMILARITY_HIGH_THRESHOLD
SIMILARITY_MODERATE_THRESHOLD: float = settings.SIMILARITY_MODERATE_THRESHOLD
USER_AGENT: str = settings.USER_AGENT
REQUEST_TIMEOUT: float = settings.REQUEST_TIMEOUT
MIN_POST_LENGTH: int = settings.MIN_POST_LENGTH
EITAA_BASE_URL: str = settings.EITAA_BASE_URL
BALE_BASE_URL: str = settings.BALE_BASE_URL
DEFAULT_EITAA_CHANNEL: str = settings.DEFAULT_EITAA_CHANNEL
DEFAULT_BALE_CHANNEL: str = settings.DEFAULT_BALE_CHANNEL
POPULAR_CHANNELS: Dict[str, List[str]] = settings.POPULAR_CHANNELS

__all__ = [
    "Settings",
    "settings",
    "EMBEDDING_MODEL_NAME",
    "SIMILARITY_HIGH_THRESHOLD",
    "SIMILARITY_MODERATE_THRESHOLD",
    "USER_AGENT",
    "REQUEST_TIMEOUT",
    "MIN_POST_LENGTH",
    "EITAA_BASE_URL",
    "BALE_BASE_URL",
    "DEFAULT_EITAA_CHANNEL",
    "DEFAULT_BALE_CHANNEL",
    "POPULAR_CHANNELS",
    "NEWS_AGENCIES",
    "get_channel_display_name",
]

