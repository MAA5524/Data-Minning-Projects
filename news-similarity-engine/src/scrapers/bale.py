"""Bale public channel scraper."""

from typing import List, Set
from bs4 import BeautifulSoup, Tag

import config
from src.scrapers.base import BaseScraper, ScraperError


class BaleScraper(BaseScraper):
    """Asynchronous scraper for public Bale (ble.ir) channel web preview pages."""

    # Candidate CSS selectors commonly used across Bale web preview versions
    PRIMARY_SELECTORS = [
        "div[class*='message-text']",
        "div[class*='message_text']",
        "div[class*='bubble-text']",
        "div[class*='messageBubble']",
        "div[class*='public-message']",
        "div[class*='messageContent']",
        "div[class*='messageItem']",
        "div[class*='message-container']",
        "p[class*='message']",
        "p[class*='text']",
    ]

    async def fetch_posts(self, channel: str, limit: int = 10) -> List[str]:
        """Fetch latest posts from public Bale channel.

        Args:
            channel: Bale channel username or link (e.g. 'iribnews' or '@iribnews').
            limit: Maximum number of latest posts to return.

        Returns:
            List of extracted news post texts.

        Raises:
            ScraperError: If scraping fails due to network or parsing errors.
        """
        clean_channel = self.sanitize_channel(channel)
        if not clean_channel:
            raise ScraperError("Bale channel ID cannot be empty.")

        url = f"{config.BALE_BASE_URL}/{clean_channel}"
        html_content = await self.get_html(url)

        return self.parse_posts(html_content, limit=limit)

    def parse_posts(self, html_content: str, limit: int = 10) -> List[str]:
        """Parse Bale HTML content to extract public post messages with fallback selectors.

        Args:
            html_content: Raw HTML text from Bale channel web preview.
            limit: Maximum number of posts to retrieve.

        Returns:
            List of post texts.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip scripts, styles, headers, and navigation to avoid scraping UI chrome
        for unwanted in soup.find_all(["script", "style", "nav", "header", "footer", "button"]):
            unwanted.decompose()

        # Step 1: Attempt extraction with primary class selectors
        candidate_nodes: List[Tag] = []
        for selector in self.PRIMARY_SELECTORS:
            nodes = soup.select(selector)
            if nodes:
                candidate_nodes.extend(nodes)

        posts: List[str] = []
        seen_texts: Set[str] = set()

        if candidate_nodes:
            # Process candidate nodes in reverse (newest posts at the bottom)
            for node in reversed(candidate_nodes):
                for br in node.find_all("br"):
                    br.replace_with(" ")

                text = node.get_text(separator=" ", strip=True)
                if len(text) >= config.MIN_POST_LENGTH and text not in seen_texts:
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        break

        # Step 2: Fallback extraction if primary selectors yield insufficient posts
        if len(posts) < limit:
            # Fallback to paragraph or div blocks containing substantial Persian text
            fallback_blocks = soup.find_all(["p", "div", "article"])
            for block in reversed(fallback_blocks):
                # Avoid parent nodes that contain already collected nodes
                for br in block.find_all("br"):
                    br.replace_with(" ")

                text = block.get_text(separator=" ", strip=True)

                # Heuristic: must be long enough and not already recorded or substring of recorded
                if (
                    len(text) >= config.MIN_POST_LENGTH
                    and text not in seen_texts
                    and not any(text in existing for existing in seen_texts)
                ):
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        break

        return posts
