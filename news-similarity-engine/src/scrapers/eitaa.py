"""Eitaa public channel scraper."""

from typing import List
from bs4 import BeautifulSoup

import config
from src.scrapers.base import BaseScraper, ScraperError


class EitaaScraper(BaseScraper):
    """Asynchronous scraper for public Eitaa channel web preview pages."""

    async def fetch_posts(self, channel: str, limit: int = 10) -> List[str]:
        """Fetch latest posts from public Eitaa channel.

        Args:
            channel: Eitaa channel ID or link (e.g., 'farsna' or '@farsna').
            limit: Maximum number of latest posts to return.

        Returns:
            List of extracted news post texts.

        Raises:
            ScraperError: If scraping fails due to network or parsing issues.
        """
        clean_channel = self.sanitize_channel(channel)
        if not clean_channel:
            raise ScraperError("Eitaa channel ID cannot be empty.")

        url = f"{config.EITAA_BASE_URL}/{clean_channel}"
        html_content = await self.get_html(url)

        return self.parse_posts(html_content, limit=limit)

    def parse_posts(self, html_content: str, limit: int = 10) -> List[str]:
        """Parse Eitaa HTML content to extract public post messages.

        Args:
            html_content: Raw HTML text from Eitaa web page.
            limit: Maximum number of posts to retrieve.

        Returns:
            List of post texts.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Public Eitaa channel posts reside in div.eitaa_message_text
        message_nodes = soup.select("div.eitaa_message_text")

        posts: List[str] = []
        # Reverse to get newest posts first (messages in web preview are ordered chronologically)
        for node in reversed(message_nodes):
            # Replace <br> tags with spaces before extracting text to prevent concatenated words
            for br in node.find_all("br"):
                br.replace_with(" ")

            text = node.get_text(separator=" ", strip=True)

            # Filter out captions shorter than minimum threshold (media-only, sticker, or empty)
            if len(text) >= config.MIN_POST_LENGTH and text not in posts:
                posts.append(text)
                if len(posts) >= limit:
                    break

        return posts
