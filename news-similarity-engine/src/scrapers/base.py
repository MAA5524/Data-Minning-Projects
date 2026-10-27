"""Base asynchronous scraper module."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import httpx

import config


class ScraperError(Exception):
    """Base exception for scraper operations."""
    pass


class ChannelNotFoundError(ScraperError):
    """Raised when a public channel returns 404 or does not exist."""
    pass


class RateLimitError(ScraperError):
    """Raised when request rate limits (HTTP 429) are encountered."""
    pass


class BaseScraper(ABC):
    """Abstract base scraper providing async HTTP handling with modern browser headers."""

    def __init__(self, timeout: float = config.REQUEST_TIMEOUT) -> None:
        """Initialize the scraper.

        Args:
            timeout: Request timeout in seconds.
        """
        self.timeout = timeout
        self.headers: Dict[str, str] = {
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fa,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not A(Brand";v="8", "Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def sanitize_channel(self, channel: str) -> str:
        """Sanitize channel ID by stripping leading @, URLs, and slashes.

        Args:
            channel: Raw channel string (e.g. '@farsna', 'https://eitaa.com/farsna/').

        Returns:
            Clean channel identifier.
        """
        ch = channel.strip()
        # Remove full URL prefixes if pasted
        for prefix in ["https://eitaa.com/", "http://eitaa.com/", "https://ble.ir/", "http://ble.ir/"]:
            if ch.lower().startswith(prefix):
                ch = ch[len(prefix):]
        # Strip @ and slashes
        ch = ch.lstrip("@").strip("/")
        return ch

    async def get_html(self, url: str) -> str:
        """Safely fetch HTML content from a target URL.

        Args:
            url: Target URL string.

        Returns:
            Decoded HTML response text.

        Raises:
            ChannelNotFoundError: If HTTP 404 is encountered.
            RateLimitError: If HTTP 429 is encountered.
            ScraperError: On generic connection failure or invalid status.
        """
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                
                if response.status_code == 404:
                    raise ChannelNotFoundError(f"Channel not found at {url} (HTTP 404)")
                elif response.status_code == 429:
                    raise RateLimitError(f"Rate limited while requesting {url} (HTTP 429)")
                elif response.is_error:
                    raise ScraperError(
                        f"Failed to fetch {url}: HTTP {response.status_code} {response.reason_phrase}"
                    )

                return response.text

        except httpx.TimeoutException as exc:
            raise ScraperError(f"Timeout while connecting to {url}: {exc}") from exc
        except httpx.RequestError as exc:
            raise ScraperError(f"Network error while connecting to {url}: {exc}") from exc

    @abstractmethod
    async def fetch_posts(self, channel: str, limit: int = 10) -> List[str]:
        """Fetch cleaned string content of latest posts from a channel.

        Args:
            channel: Target channel username.
            limit: Maximum number of posts to retrieve.

        Returns:
            List of post strings.
        """
        pass
