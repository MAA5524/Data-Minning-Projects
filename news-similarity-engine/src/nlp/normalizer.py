"""Persian text normalization module."""

import re
import unicodedata
from typing import Dict


class PersianNormalizer:
    """Normalizes Persian and Arabic character discrepancies, diacritics, and whitespace."""

    # Arabic to Persian character mapping
    CHAR_MAPPING: Dict[str, str] = {
        # Arabic Yeh variants -> Persian Yeh
        "\u064a": "\u06cc",  # ي -> ی
        "\u0649": "\u06cc",  # ى -> ی
        "\u06d2": "\u06cc",  # ے -> ی
        # Arabic Kaf variants -> Persian Kaf
        "\u0643": "\u06a9",  # ك -> ک
        "\u06aa": "\u06a9",  # ڪ -> ک
        # Teh Marbuta -> Heh
        "\u0629": "\u0647",  # ة -> ه
        "\u06c0": "\u0647",  # ۀ -> ه
        # Arabic digits to Persian digits or standardized (can also retain/standardize)
        "\u0660": "\u06f0",
        "\u0661": "\u06f1",
        "\u0662": "\u06f2",
        "\u0663": "\u06f3",
        "\u0664": "\u06f4",
        "\u0665": "\u06f5",
        "\u0666": "\u06f6",
        "\u0667": "\u06f7",
        "\u0668": "\u06f8",
        "\u0669": "\u06f9",
    }

    # Regex for consecutive ZWNJ
    MULTIPLE_ZWNJ_REGEX = re.compile(r"\u200c+")
    # ZWNJ adjacent to whitespace
    ZWNJ_WHITESPACE_REGEX = re.compile(r"(\s+\u200c|\u200c\s+)")
    # Multiple whitespace characters (spaces, tabs, newlines, non-breaking spaces)
    MULTIPLE_SPACES_REGEX = re.compile(r"[\s\u00a0\u2000-\u200b\u202f]+")

    def __init__(self) -> None:
        """Initialize the normalizer with compiled translation table."""
        self.trans_table = str.maketrans(self.CHAR_MAPPING)

    def strip_diacritics(self, text: str) -> str:
        """Strip Arabic/Persian diacritics (Tashdeed, Tanwin, Kasrah, Fathah, Dammah, Sukun).

        Args:
            text: Input string.

        Returns:
            String with non-spacing diacritics removed.
        """
        # Decompose unicode and remove non-spacing mark (Mn) category characters
        # that belong to Arabic/Persian diacritics
        chars = []
        for ch in text:
            category = unicodedata.category(ch)
            # Remove combining diacritical marks (Mn) like Tashdeed (\u0651), Fathah (\u064e), etc.
            if category == "Mn":
                continue
            chars.append(ch)
        return "".join(chars)

    def normalize(self, text: str) -> str:
        """Normalize Persian/Arabic characters, strip diacritics, and standardize whitespace.

        Args:
            text: Raw Persian/Arabic text.

        Returns:
            Normalized Persian text string.
        """
        if not text:
            return ""

        # Step 1: Replace Arabic-specific characters with Persian counterparts
        normalized = text.translate(self.trans_table)

        # Step 2: Strip diacritics / Erab / Tashdeed / Tanwin using unicodedata
        normalized = self.strip_diacritics(normalized)

        # Step 3: Standardize Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله)
        normalized = self.MULTIPLE_ZWNJ_REGEX.sub("\u200c", normalized)
        normalized = self.ZWNJ_WHITESPACE_REGEX.sub(" ", normalized)
        normalized = normalized.strip("\u200c")

        # Step 4: Standardize consecutive spaces, tabs, and newlines to a single space
        normalized = self.MULTIPLE_SPACES_REGEX.sub(" ", normalized)

        return normalized.strip()
