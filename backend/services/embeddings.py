"""
Embeddings service for generating vector embeddings using sentence-transformers.
Supports semantic search functionality.
"""

import json
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Lazy import - will be imported only when needed
_embeddings_model = None


def get_embeddings_model():
    """Lazy load embeddings model to avoid loading until first use."""
    global _embeddings_model
    if _embeddings_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
            _embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"Model loaded. Embedding dimension: {_embeddings_model.get_sentence_embedding_dimension()}")
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
    return _embeddings_model


class EmbeddingsService:
    """Service for generating and managing vector embeddings."""

    EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 output dimension
    SIMILARITY_THRESHOLD = 0.7  # Default threshold for similarity matching

    @staticmethod
    def generate_embedding(text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding, or None if generation fails
        """
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text for embedding: {text}")
            return None

        try:
            model = get_embeddings_model()
            embedding = model.encode(text, convert_to_tensor=False)
            # Convert numpy array to Python list for JSON serialization
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        except Exception as e:
            logger.error(f"Error generating embedding: {type(e).__name__}: {str(e)}")
            return None

    @staticmethod
    def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (None for failed texts)
        """
        if not texts:
            return []

        try:
            model = get_embeddings_model()
            embeddings = model.encode(texts, convert_to_tensor=False)
            # Convert to list of lists for JSON serialization
            return [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {type(e).__name__}: {str(e)}")
            return [None] * len(texts)

    @staticmethod
    def embedding_to_json(embedding: List[float]) -> str:
        """Serialize embedding to JSON for database storage."""
        return json.dumps(embedding)

    @staticmethod
    def embedding_from_json(json_str: Optional[str]) -> Optional[List[float]]:
        """Deserialize embedding from JSON database storage."""
        if not json_str:
            return None
        try:
            embedding = json.loads(json_str)
            if isinstance(embedding, list) and all(isinstance(x, (int, float)) for x in embedding):
                return embedding
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Error deserializing embedding: {e}")
        return None

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1, vec2: Lists of floats representing vectors

        Returns:
            Similarity score between -1 and 1 (typically 0 to 1 for normalized embeddings)
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            # Handle zero vectors
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = np.dot(v1, v2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    @staticmethod
    def find_similar(
        query_embedding: List[float],
        candidate_embeddings: List[tuple],  # [(term_id, embedding_json), ...]
        threshold: float = SIMILARITY_THRESHOLD,
        top_k: int = 5
    ) -> List[dict]:
        """
        Find similar embeddings from candidates using cosine similarity.

        Args:
            query_embedding: The query embedding vector
            candidate_embeddings: List of (id, embedding_json) tuples
            threshold: Minimum similarity score to include
            top_k: Maximum number of results to return

        Returns:
            List of dicts with term_id and similarity score, sorted by similarity (descending)
        """
        results = []

        for term_id, embedding_json in candidate_embeddings:
            candidate_embedding = EmbeddingsService.embedding_from_json(embedding_json)
            if not candidate_embedding:
                continue

            similarity = EmbeddingsService.cosine_similarity(query_embedding, candidate_embedding)

            if similarity >= threshold:
                results.append({
                    'term_id': term_id,
                    'similarity_score': round(similarity, 4)
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Return top-k
        return results[:top_k]


# Create singleton instance
embeddings_service = EmbeddingsService()
