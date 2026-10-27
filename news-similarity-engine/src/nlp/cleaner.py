"""Persian text cleaning module."""

import re
import string
from typing import Final, FrozenSet


class TextCleaner:
    """Cleans raw text by stripping URLs, mentions, emojis, numbers, and typography."""

    # Persian and standard punctuation set
    PERSIAN_PUNCTUATION: Final[FrozenSet[str]] = frozenset(
        {
            "،", "؛", "؟", "«", "»", "ـ", "٫", "٬", "٪",
            "!", "?", ".", "*", "(", ")", ":", ";", ",",
            '"', "'", "/", "\\", "[", "]", "{", "}", "_",
            "-", "+", "=", "<", ">", "~", "^", "%", "$",
            "#", "@", "|", "&", "`", "…"
        } | set(string.punctuation)
    )

    # Regex patterns
    URL_REGEX = re.compile(
        r"(https?://\S+|www\.\S+|t\.me/\S+|eitaa\.com/\S+|ble\.ir/\S+)",
        flags=re.IGNORECASE,
    )
    MENTION_REGEX = re.compile(r"@[\w\._\-]+", flags=re.UNICODE)
    EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+", flags=re.IGNORECASE)
    HTML_TAG_REGEX = re.compile(r"<[^>]+>|&[a-zA-Z0-9#]+;")
    
    # Digits: Persian (۰-۹), Arabic-Indic (٠-٩), and English (0-9)
    DIGIT_REGEX = re.compile(r"[\u06f0-\u06f9\u0660-\u06690-9]+")

    # Emoji ranges
    EMOJI_REGEX = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "\U00002600-\U000026FF"  # misc symbols
        "]+",
        flags=re.UNICODE,
    )

    # Allowed characters: Persian & Arabic letters, English letters, and ZWNJ (\u200c)
    # Excludes punctuation, symbols, numbers, and diacritics.
    ALLOWED_CHARS_REGEX = re.compile(
        r"[^\u0621-\u0628\u062a-\u063a\u0641-\u0642\u0644-\u0648\u067e\u0686\u0698\u06af\u06cc\u06a9\u0622\u0623\u0624\u0625\u0626\u06c0a-zA-Z\u200c\s]"
    )

    MULTIPLE_SPACES_REGEX = re.compile(r"\s+")

    def clean(self, text: str) -> str:
        """Strip URLs, mentions, emails, emojis, punctuation, and digits.

        Retains Persian and English alphabetic characters and zero-width spaces.

        Args:
            text: Raw input text string.

        Returns:
            Cleaned and normalized string.
        """
        if not text:
            return ""

        # Step 1: Remove HTML tags and entities
        cleaned = self.HTML_TAG_REGEX.sub(" ", text)

        # Step 2: Strip URLs
        cleaned = self.URL_REGEX.sub(" ", cleaned)

        # Step 3: Strip mentions (@...) and emails
        cleaned = self.EMAIL_REGEX.sub(" ", cleaned)
        cleaned = self.MENTION_REGEX.sub(" ", cleaned)

        # Step 4: Strip Emojis
        cleaned = self.EMOJI_REGEX.sub(" ", cleaned)

        # Step 5: Strip digits (English, Persian, Arabic)
        cleaned = self.DIGIT_REGEX.sub(" ", cleaned)

        # Step 6: Filter non-allowed characters (punctuation, stray symbols)
        cleaned = self.ALLOWED_CHARS_REGEX.sub(" ", cleaned)

        # Step 7: Collapse multiple spaces and trim
        cleaned = self.MULTIPLE_SPACES_REGEX.sub(" ", cleaned)

        return cleaned.strip()
