"""Unit tests for Eitaa and Bale scrapers."""

import pytest
from src.scrapers.eitaa import EitaaScraper
from src.scrapers.bale import BaleScraper
from src.scrapers.base import ScraperError


MOCK_EITAA_HTML = """
<!DOCTYPE html>
<html>
<head><title>Eitaa Preview</title></head>
<body>
    <div class="eitaa_message_wrap">
        <div class="eitaa_message_text">
            کوتاه
        </div>
    </div>
    <div class="eitaa_message_wrap">
        <div class="eitaa_message_text">
            خبر اول: نرخ تورم سالانه در اردیبهشت ماه با کاهش قابل توجه به رقم ۳۵ درصد رسید و روند نزولی ادامه دارد.
        </div>
    </div>
    <div class="eitaa_message_wrap">
        <div class="eitaa_message_text">
            خبر دوم: سازمان هواشناسی اعلام کرد<br>سامانه بارشی جدید به زودی وارد کشور خواهد شد و بارش‌ها گسترش می‌یابد.
        </div>
    </div>
</body>
</html>
"""

MOCK_BALE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Bale Preview</title></head>
<body>
    <header><p>منوی بالا سایت که نباید واکشی شود چون هدر است</p></header>
    <div class="messageItem">
        <div class="messageBubble">
            <div class="message-text">
                گزارش بانک مرکزی: تسهیلات پرداختی به بخش مسکن و تولید در شش ماهه نخست سال رشد چشمگیری را ثبت کرد.
            </div>
        </div>
    </div>
    <div class="messageItem">
        <div class="messageBubble">
            <div class="message-text">
                خیلی کوتاه
            </div>
        </div>
    </div>
    <div class="messageItem">
        <div class="messageBubble">
            <div class="message-text">
                سازمان هواشناسی کشور نسبت به وقوع سیلاب در ۱۰ استان کشور هشدار جدی صادر نمود و بر لزوم احتیاط تاکید کرد.
            </div>
        </div>
    </div>
    <footer><p>فوتر سایت</p></footer>
</body>
</html>
"""


class TestScrapers:
    """Test suite for scraping public web preview pages."""

    def test_eitaa_channel_sanitization(self) -> None:
        scraper = EitaaScraper()
        assert scraper.sanitize_channel("@farsna") == "farsna"
        assert scraper.sanitize_channel("https://eitaa.com/farsna/") == "farsna"
        assert scraper.sanitize_channel("   @tasnimnews/  ") == "tasnimnews"

    def test_eitaa_parse_posts(self) -> None:
        scraper = EitaaScraper()
        posts = scraper.parse_posts(MOCK_EITAA_HTML, limit=10)

        # "کوتاه" should be filtered out by MIN_POST_LENGTH (35 chars)
        assert len(posts) == 2
        # Verify newest post is first (order reversed)
        assert "خبر دوم" in posts[0]
        assert "خبر اول" in posts[1]
        # Verify <br> replaced with space
        assert "اعلام کرد سامانه" in posts[0]

    def test_eitaa_parse_posts_limit(self) -> None:
        scraper = EitaaScraper()
        posts = scraper.parse_posts(MOCK_EITAA_HTML, limit=1)
        assert len(posts) == 1

    def test_bale_channel_sanitization(self) -> None:
        scraper = BaleScraper()
        assert scraper.sanitize_channel("@iribnews") == "iribnews"
        assert scraper.sanitize_channel("https://ble.ir/iribnews/") == "iribnews"

    def test_bale_parse_posts(self) -> None:
        scraper = BaleScraper()
        posts = scraper.parse_posts(MOCK_BALE_HTML, limit=10)

        # "خیلی کوتاه" should be filtered out, header/footer stripped
        assert len(posts) == 2
        assert any("تسهیلات پرداختی" in p for p in posts)
        assert any("سازمان هواشناسی کشور" in p for p in posts)

    def test_bale_fallback_parsing(self) -> None:
        fallback_html = """
        <div>
            <p>این یک خبر آزمایشی با ساختار متفاوت در صفحات بله است که شامل متنی طولانی جهت تست استخراج است.</p>
        </div>
        """
        scraper = BaleScraper()
        posts = scraper.parse_posts(fallback_html, limit=5)
        assert len(posts) == 1
        assert "خبر آزمایشی" in posts[0]
