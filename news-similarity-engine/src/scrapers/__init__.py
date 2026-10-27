"""Scrapers subpackage for Eitaa and Bale platforms."""

from src.scrapers.base import BaseScraper, ScraperError, ChannelNotFoundError, RateLimitError
from src.scrapers.eitaa import EitaaScraper
from src.scrapers.bale import BaleScraper

__all__ = [
    "BaseScraper",
    "ScraperError",
    "ChannelNotFoundError",
    "RateLimitError",
    "EitaaScraper",
    "BaleScraper",
]
