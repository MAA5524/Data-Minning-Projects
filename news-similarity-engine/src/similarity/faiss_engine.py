"""Dense semantic embeddings and FAISS similarity engine."""

from typing import Any, List, Optional, Tuple
import numpy as np

try:
    import faiss
    FaissIndexType = faiss.IndexFlatIP
except ImportError:
    faiss = None
    FaissIndexType = Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

import config


class FaissSimilarityEngine:
    """Computes semantic similarity using dense sentence embeddings and FAISS index."""

    def __init__(self, model_name: str = config.EMBEDDING_MODEL_NAME) -> None:
        """Initialize the sentence transformer model and retrieve vector dimension.

        Args:
            model_name: Hugging Face model identifier (e.g. 'BAAI/bge-m3').
        """
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is required for FaissSimilarityEngine. "
                "Please install it with: pip install sentence-transformers"
            )
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        # Dimension D of the embedding space (supporting modern and legacy sentence-transformers)
        if hasattr(self.model, "get_embedding_dimension"):
            self.dimension: int = self.model.get_embedding_dimension()
        else:
            self.dimension: int = self.model.get_sentence_embedding_dimension()

    @staticmethod
    def map_cosine_to_percentage(cosine_val: float) -> float:
        """Map raw cosine similarity from [-1.0, 1.0] to bounded [0.0, 1.0].

        Args:
            cosine_val: Raw inner product or cosine similarity float.

        Returns:
            Normalized similarity score in range [0.0, 1.0].
        """
        normalized = (cosine_val + 1.0) / 2.0
        return float(np.clip(normalized, 0.0, 1.0))

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode text strings into L2-normalized float32 embeddings.

        Args:
            texts: List of text strings.

        Returns:
            Numpy 2D array of shape (N, dimension) with dtype float32.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def build_index(self, documents: List[str]) -> Tuple["faiss.IndexFlatIP", np.ndarray]:
        """Encode documents and build an Inner-Product (Cosine) FAISS index.

        Args:
            documents: List of candidate post texts.

        Returns:
            Tuple of (faiss.IndexFlatIP, numpy embeddings array).
        """
        if faiss is None:
            raise ImportError(
                "faiss is required for FaissSimilarityEngine. "
                "Please install it with: pip install faiss-cpu"
            )
        index = faiss.IndexFlatIP(self.dimension)
        if not documents:
            return index, np.empty((0, self.dimension), dtype=np.float32)

        embeddings = self.encode(documents)
        index.add(embeddings)
        return index, embeddings

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Compute semantic cosine similarity between two texts.

        Encodes both texts with L2 normalization and maps inner product from [-1.0, 1.0]
        to [0.0, 1.0].

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            Similarity score bounded between 0.0 and 1.0.
        """
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        vecs = self.encode([text_a, text_b])
        # Inner product of normalized vectors equals cosine similarity
        raw_cos = float(np.dot(vecs[0], vecs[1]))
        return self.map_cosine_to_percentage(raw_cos)

    def search_top_k(
        self,
        index: FaissIndexType,
        query: str,
        top_k: int = 1,
    ) -> List[Tuple[int, float]]:
        """Query FAISS index for the top-k most semantically similar documents.

        Args:
            index: Pre-built faiss.IndexFlatIP index.
            query: Query text string.
            top_k: Number of nearest neighbors to retrieve.

        Returns:
            List of (document_index, mapped_similarity_score) sorted by relevance.
        """
        if not query or not query.strip() or index.ntotal == 0 or top_k <= 0:
            return []

        query_vec = self.encode([query])
        k = min(top_k, index.ntotal)
        scores, indices = index.search(query_vec, k)

        results: List[Tuple[int, float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx != -1:
                mapped_score = self.map_cosine_to_percentage(float(score))
                results.append((int(idx), mapped_score))

        return results
