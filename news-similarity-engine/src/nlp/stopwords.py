"""Persian stopwords filtering module."""

from typing import Final, FrozenSet, List


class StopwordFilter:
    """Filters Persian stopwords and single-character stray tokens."""

    # Internal frozen set of 120+ common Persian stopwords
    STOPWORDS: Final[FrozenSet[str]] = frozenset(
        {
            # Prepositions and conjunctions
            "از", "به", "در", "با", "که", "این", "آن", "برای", "را", "تا",
            "یک", "بر", "نیز", "شد", "است", "بود", "شود", "هم", "می", "دیگر",
            "وی", "او", "شدند", "گفت", "کرد", "پس", "چون", "اگر", "یا", "ولی",
            "اما", "هر", "چه", "بی", "هیچ", "باید", "شاید", "نیست", "بوده",
            "باشد", "دارند", "دارد", "داشت", "داشته", "کنند", "کند", "کرده",
            "بین", "زیر", "روی", "پیش", "میان", "خود", "خودشان", "خودت", "خودم",
            "ما", "شما", "آنها", "ایشان", "همه", "برخی", "بعضی", "چند", "چنین",
            "چنان", "حتی", "بلکه", "بنابراین", "زیرا", "چرا", "وقتی", "زمانی",
            "جایی", "بسیار", "خیلی", "کمتر", "بیشتر", "اول", "دوم", "سوم", "هنوز",
            "فقط", "تنها", "درباره", "نسبت", "طبق", "مانند", "مثل", "یعنی", "ضمن",
            "بله", "خیر", "نه", "کدام", "اکنون", "سپس", "همواره", "همیشه", "بدون",
            "توسط", "جهت", "تمام", "کلیه", "اینکه", "آنکه", "بدین", "بدان", "همین",
            "همان", "گرچه", "چنانچه", "زیراکه", "طریق", "هنگام", "هنگامی", "حال",
            "حالی", "مورد", "پیرامون", "دوباره", "بار", "مجدد", "مجددا", "غالبا",
            "حدود", "قریب", "نزدیک", "علاوه", "همچنین", "برابر", "نزد", "نزدیک",
            "پشت", "کنار", "بالا", "پایین", "بیش", "کم", "اندک", "زیاد", "چطور",
            "چگونه", "کجا", "کی", "آنچه", "اینها", "آنان", "یکی", "دگری", "کس",
            "کسی", "هیچکس", "همهکس", "چیز", "چیزی", "سایر", "دیگری", "طرف", "سوی"
        }
    )

    def __init__(self, additional_stopwords: FrozenSet[str] = frozenset()) -> None:
        """Initialize the filter with optional additional stopwords.

        Args:
            additional_stopwords: Additional words to exclude.
        """
        if additional_stopwords:
            self.stopwords = self.STOPWORDS | additional_stopwords
        else:
            self.stopwords = self.STOPWORDS

    def filter_tokens(self, text: str) -> str:
        """Filter out stopwords and single-character stray letters.

        Args:
            text: Normalized and cleaned input text string.

        Returns:
            Space-separated string of informative tokens.
        """
        if not text:
            return ""

        tokens: List[str] = text.split()
        filtered_tokens: List[str] = [
            token
            for token in tokens
            if len(token) > 1 and token not in self.stopwords
        ]

        return " ".join(filtered_tokens)
