"""Unit tests for Persian NLP preprocessing modules."""

import pytest
from src.nlp.normalizer import PersianNormalizer
from src.nlp.cleaner import TextCleaner
from src.nlp.stopwords import StopwordFilter
from src.nlp import PersianNLPPipeline


class TestPersianNormalizer:
    """Test suite for PersianNormalizer."""

    @pytest.fixture
    def normalizer(self) -> PersianNormalizer:
        return PersianNormalizer()

    def test_arabic_yeh_and_kaf_normalization(self, normalizer: PersianNormalizer) -> None:
        """Verify Arabic Yeh (\u064a) and Kaf (\u0643) convert to Persian counterparts."""
        arabic_text = "شركت‌هاي دولتي كشور"
        expected = "شرکت‌های دولتی کشور"
        assert normalizer.normalize(arabic_text) == expected

    def test_teh_marbuta_conversion(self, normalizer: PersianNormalizer) -> None:
        """Verify Arabic Teh Marbuta (\u0629) converts to Persian Heh (\u0647)."""
        arabic_text = "جامعة المصطفی"
        assert "جامعه" in normalizer.normalize(arabic_text)

    def test_diacritics_and_erab_stripping(self, normalizer: PersianNormalizer) -> None:
        """Verify Tashdeed, Tanwin, Kasrah, Fathah, Dammah are cleanly removed."""
        text_with_erab = "مُحَمَّدٌ رَسُولُ اللَّهِ"
        result = normalizer.normalize(text_with_erab)
        assert result == "محمد رسول الله"

    def test_zwnj_standardization(self, normalizer: PersianNormalizer) -> None:
        """Verify multiple consecutive ZWNJs are collapsed to a single ZWNJ."""
        text_with_multiple_zwnj = "می\u200c\u200c\u200cرود"
        assert normalizer.normalize(text_with_multiple_zwnj) == "می\u200cرود"

    def test_whitespace_standardization(self, normalizer: PersianNormalizer) -> None:
        """Verify multiple spaces, tabs, and newlines become a single space."""
        messy_whitespace = "  خبر    مهم  \n\n\t  امروز   "
        assert normalizer.normalize(messy_whitespace) == "خبر مهم امروز"

    def test_empty_string_handling(self, normalizer: PersianNormalizer) -> None:
        """Verify empty and whitespace inputs return empty string."""
        assert normalizer.normalize("") == ""
        assert normalizer.normalize("    ") == ""


class TestTextCleaner:
    """Test suite for TextCleaner."""

    @pytest.fixture
    def cleaner(self) -> TextCleaner:
        return TextCleaner()

    def test_url_removal(self, cleaner: TextCleaner) -> None:
        """Verify URLs (http, https, t.me, eitaa.com) are stripped."""
        text = "جزئیات خبر در https://eitaa.com/farsna/1234 و https://ble.ir/iribnews منتشر شد."
        cleaned = cleaner.clean(text)
        assert "https://" not in cleaned
        assert "eitaa.com" not in cleaned
        assert "ble.ir" not in cleaned
        assert "جزئیات خبر در" in cleaned

    def test_mentions_and_emails_removal(self, cleaner: TextCleaner) -> None:
        """Verify @mentions and email addresses are stripped."""
        text = "ارتباط با ادمین @farsna_admin یا ایمیل info@farsnews.ir صورت گیرد."
        cleaned = cleaner.clean(text)
        assert "@farsna_admin" not in cleaned
        assert "info@farsnews.ir" not in cleaned

    def test_punctuation_and_typography_removal(self, cleaner: TextCleaner) -> None:
        """Verify Persian and English typography marks are stripped."""
        text = "آیا شاخص بورس رشد کرد؟ «بله!» قیمت: ۱۰۰۰ ریال؛ تمام."
        cleaned = cleaner.clean(text)
        for mark in ["؟", "«", "»", "!", ":", "؛", "."]:
            assert mark not in cleaned

    def test_digit_removal(self, cleaner: TextCleaner) -> None:
        """Verify Persian, Arabic, and English digits are removed."""
        text = "رشد ۱۲ درصدی با 450 میلیارد تومان در سال ۱۴۰۳"
        cleaned = cleaner.clean(text)
        assert "۱۲" not in cleaned
        assert "450" not in cleaned
        assert "۱۴۰۳" not in cleaned
        assert "رشد" in cleaned
        assert "درصدی با" in cleaned

    def test_emoji_removal(self, cleaner: TextCleaner) -> None:
        """Verify emojis are stripped."""
        text = "خبر فوری 🚨⚠️ پیروزی تیم ملی 🇮🇷🎉"
        cleaned = cleaner.clean(text)
        assert "🚨" not in cleaned
        assert "⚠️" not in cleaned
        assert "🇮🇷" not in cleaned
        assert "خبر فوری پیروزی تیم ملی" in cleaned

    def test_zwnj_retention(self, cleaner: TextCleaner) -> None:
        """Verify valid ZWNJ within words is retained."""
        text = "می‌خواهیم پروژه‌های جدید بسازیم"
        cleaned = cleaner.clean(text)
        assert "\u200c" in cleaned
        assert "می‌خواهیم" in cleaned


class TestStopwordFilter:
    """Test suite for StopwordFilter."""

    @pytest.fixture
    def filter(self) -> StopwordFilter:
        return StopwordFilter()

    def test_removes_common_stopwords(self, filter: StopwordFilter) -> None:
        """Verify common Persian stopwords like از, به, در, که are filtered."""
        text = "دولت از طرح جدید در مجلس که برای مردم بود حمایت کرد"
        filtered = filter.filter_tokens(text)
        for stopword in ["از", "در", "که", "برای", "بود", "کرد"]:
            assert stopword not in filtered.split()
        assert "دولت" in filtered
        assert "طرح" in filtered
        assert "جدید" in filtered
        assert "مجلس" in filtered
        assert "مردم" in filtered
        assert "حمایت" in filtered

    def test_removes_single_character_stray_letters(self, filter: StopwordFilter) -> None:
        """Verify single-character tokens (e.g. stray و or ا) are discarded."""
        text = "ایران و روسیه پیرامون مسائل اقتصادی گفتگو کردند"
        filtered = filter.filter_tokens(text)
        assert "و" not in filtered.split()
        assert "ایران" in filtered
        assert "روسیه" in filtered

    def test_empty_input(self, filter: StopwordFilter) -> None:
        """Verify empty input returns empty string."""
        assert filter.filter_tokens("") == ""


class TestNLPPipeline:
    """Integration test for PersianNLPPipeline."""

    def test_end_to_end_pipeline(self) -> None:
        pipeline = PersianNLPPipeline()
        raw = "بانك مركزي در https://cbi.ir اعلام كرد: نرخ تورّم ۱۲٪ كاهش يافت! 🚀 @cbi_news"
        transformed = pipeline.transform(raw)
        
        # Arabic characters converted
        assert "ك" not in transformed
        assert "ي" not in transformed
        # Digits and symbols removed
        assert "۱۲" not in transformed
        assert "%" not in transformed
        assert "٪" not in transformed
        assert "!" not in transformed
        assert "🚀" not in transformed
        # Stopwords removed
        assert "در" not in transformed.split()
        # Informative keywords preserved
        assert "بانک" in transformed
        assert "مرکزی" in transformed
        assert "اعلام" in transformed
        assert "نرخ" in transformed
        assert "تورم" in transformed
        assert "کاهش" in transformed
        assert "یافت" in transformed
