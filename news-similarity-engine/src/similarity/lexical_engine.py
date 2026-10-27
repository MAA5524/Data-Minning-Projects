"""Lexical TF-IDF and Cosine Similarity engine."""

from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LexicalSimilarityEngine:
    """Computes lexical similarity using TF-IDF token vectorization and cosine similarity."""

    def __init__(self) -> None:
        """Initialize the lexical similarity engine."""
        pass

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute lexical TF-IDF cosine similarity between two cleaned texts.

        Gracefully handles edge cases such as empty strings, single characters,
        or inputs containing no valid vocabulary.

        Args:
            text_a: First cleaned text string.
            text_b: Second cleaned text string.

        Returns:
            Cosine similarity float bounded between 0.0 and 1.0.
        """
        # Edge cases: empty or whitespace-only inputs
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        try:
            # Custom token pattern to support Persian words with ZWNJ (\u200c)
            vectorizer = TfidfVectorizer(
                token_pattern=r"(?u)\b\w[\w\u200c]+\b|\b\w+\b"
            )
            tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
            
            # Check if vectorizer created any features
            if tfidf_matrix.shape[1] == 0:
                return 0.0

            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            score = float(sim_matrix[0, 0])

            # Ensure valid numerical value bounded between 0.0 and 1.0
            if np.isnan(score):
                return 0.0

            return float(np.clip(score, 0.0, 1.0))

        except (ValueError, ZeroDivisionError):
            # Empty vocabulary or stopword-only inputs raise ValueError in TfidfVectorizer
            return 0.0

    def search_top_k(
        self,
        query: str,
        documents: List[str],
        top_k: int = 1,
    ) -> List[Tuple[int, float]]:
        """Compute lexical similarity between a query and a list of documents.

        Args:
            query: Query text string.
            documents: Candidate document strings.
            top_k: Number of highest ranking documents to retrieve.

        Returns:
            List of (document_index, lexical_score) tuples sorted in descending order.
        """
        if not query or not query.strip() or not documents or top_k <= 0:
            return []

        corpus = [query] + list(documents)
        try:
            vectorizer = TfidfVectorizer(
                token_pattern=r"(?u)\b\w[\w\u200c]+\b|\b\w+\b"
            )
            tfidf_matrix = vectorizer.fit_transform(corpus)
            if tfidf_matrix.shape[1] == 0:
                return [(i, 0.0) for i in range(min(top_k, len(documents)))]

            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]
            scores = cosine_similarity(query_vec, doc_vecs)[0]

            ranked_indices = np.argsort(scores)[::-1][:top_k]
            return [
                (int(idx), float(np.clip(scores[idx], 0.0, 1.0)))
                for idx in ranked_indices
            ]
        except (ValueError, ZeroDivisionError):
            return [(i, 0.0) for i in range(min(top_k, len(documents)))]
