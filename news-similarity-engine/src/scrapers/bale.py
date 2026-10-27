"""Bale public channel scraper."""

from typing import List, Set
from bs4 import BeautifulSoup, Tag

import config
from src.scrapers.base import BaseScraper, ScraperError


class BaleScraper(BaseScraper):
    """Asynchronous scraper for public Bale (ble.ir) channel web preview pages."""

    # Candidate CSS selectors commonly used across Bale web preview versions
    PRIMARY_SELECTORS = [
        "div[class*='MessageItem_messageWrapper']",
        "div[class*='Text_text']",
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

        # Modern Bale channel preview route is at /s/{channel}
        preview_url = f"{config.BALE_BASE_URL}/s/{clean_channel}"
        try:
            html_content = await self.get_html(preview_url)
            posts = self.parse_posts(html_content, limit=limit)
            if posts:
                return posts
        except Exception:
            pass

        # Fallback to direct channel route /{channel}
        fallback_url = f"{config.BALE_BASE_URL}/{clean_channel}"
        html_content = await self.get_html(fallback_url)
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

        # Step 1: Check for message wrapper containers first
        wrapper_nodes = soup.select("div[class*='MessageItem_messageWrapper']")
        posts: List[str] = []
        seen_texts: Set[str] = set()

        # Ignore boilerplate strings that might appear in channel previews
        IGNORED_PATTERNS = ["مشاهده در وب بله", "دانلود «بله»", "پیش‌نمایش کانال"]

        if wrapper_nodes:
            # Process in chronological order or reverse to get newest
            for wrapper in reversed(wrapper_nodes):
                text_el = wrapper.select_one("div[class*='Text_text']")
                target_node = text_el if text_el else wrapper

                for br in target_node.find_all("br"):
                    br.replace_with(" ")

                text = target_node.get_text(separator=" ", strip=True)
                if any(ign in text for ign in IGNORED_PATTERNS):
                    continue

                if len(text) >= config.MIN_POST_LENGTH and text not in seen_texts:
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        return posts

        # Step 2: Attempt extraction with other primary class selectors
        candidate_nodes: List[Tag] = []
        for selector in self.PRIMARY_SELECTORS:
            nodes = soup.select(selector)
            if nodes:
                candidate_nodes.extend(nodes)

        if candidate_nodes:
            for node in reversed(candidate_nodes):
                for br in node.find_all("br"):
                    br.replace_with(" ")

                text = node.get_text(separator=" ", strip=True)
                if any(ign in text for ign in IGNORED_PATTERNS):
                    continue

                if len(text) >= config.MIN_POST_LENGTH and text not in seen_texts:
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        return posts

        # Step 3: Generic fallback to paragraph and block elements
        if not posts:
            for p_node in reversed(soup.find_all("p")):
                for br in p_node.find_all("br"):
                    br.replace_with(" ")
                text = p_node.get_text(separator=" ", strip=True)
                if any(ign in text for ign in IGNORED_PATTERNS):
                    continue
                if len(text) >= config.MIN_POST_LENGTH and text not in seen_texts:
                    seen_texts.add(text)
                    posts.append(text)
                    if len(posts) >= limit:
                        return posts

        return posts

