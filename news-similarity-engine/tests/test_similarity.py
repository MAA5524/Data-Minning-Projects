"""Unit tests for similarity engines (Lexical TF-IDF and Faiss Cosine Mapping)."""

import pytest
from src.similarity.lexical_engine import LexicalSimilarityEngine
from src.similarity.faiss_engine import FaissSimilarityEngine


class TestLexicalSimilarityEngine:
    """Test suite for LexicalSimilarityEngine."""

    @pytest.fixture
    def engine(self) -> LexicalSimilarityEngine:
        return LexicalSimilarityEngine()

    def test_identical_texts(self, engine: LexicalSimilarityEngine) -> None:
        """Identical texts should yield 1.0 (or ~1.0) cosine similarity."""
        text = "بانک مرکزی نرخ جدید سود سپرده بانکی را اعلام کرد"
        sim = engine.compute_similarity(text, text)
        assert pytest.approx(sim, 0.01) == 1.0

    def test_completely_disjoint_texts(self, engine: LexicalSimilarityEngine) -> None:
        """Texts with completely disjoint vocabulary should yield 0.0."""
        text_a = "سیب پرتقال گلابی هلو"
        text_b = "اتومبیل هواپیما قطار کشتی"
        sim = engine.compute_similarity(text_a, text_b)
        assert sim == 0.0

    def test_empty_and_whitespace_edge_cases(self, engine: LexicalSimilarityEngine) -> None:
        """Empty texts should return 0.0 without throwing exceptions."""
        assert engine.compute_similarity("", "متن نمونه") == 0.0
        assert engine.compute_similarity("    ", "متن نمونه") == 0.0
        assert engine.compute_similarity("", "") == 0.0

    def test_search_top_k(self, engine: LexicalSimilarityEngine) -> None:
        """Verify search_top_k ranks the most lexically similar document first."""
        query = "بارش باران و برف در جاده‌های کوهستانی"
        docs = [
            "نرخ جدید سود بانکی اعلام شد",
            "پیش‌بینی هواشناسی از بارش شدید برف و باران در مناطق کوهستانی",
            "صادرات نفت ایران افزایش یافت",
        ]
        results = engine.search_top_k(query, docs, top_k=2)
        assert len(results) == 2
        # Doc index 1 should be the top match
        assert results[0][0] == 1
        assert results[0][1] > 0.3


class TestFaissEngineHelpers:
    """Test suite for FaissSimilarityEngine helper functions."""

    def test_map_cosine_to_percentage(self) -> None:
        """Verify [-1.0, 1.0] maps cleanly to [0.0, 1.0]."""
        assert FaissSimilarityEngine.map_cosine_to_percentage(1.0) == 1.0
        assert FaissSimilarityEngine.map_cosine_to_percentage(-1.0) == 0.0
        assert FaissSimilarityEngine.map_cosine_to_percentage(0.0) == 0.5
        assert FaissSimilarityEngine.map_cosine_to_percentage(1.5) == 1.0
        assert FaissSimilarityEngine.map_cosine_to_percentage(-1.5) == 0.0
