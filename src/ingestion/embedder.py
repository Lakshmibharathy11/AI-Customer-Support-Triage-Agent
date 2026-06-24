# src/ingestion/embedder.py

from sentence_transformers import SentenceTransformer
import numpy as np

from src.config.settings import settings


class Embedder:
    """
    Thin wrapper around sentence-transformers.
    Loads the model once and reuses it for all embedding calls.
    """

    _instance = None  # singleton — avoid reloading the 80MB model repeatedly

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = SentenceTransformer(
                settings.EMBEDDING_MODEL
            )
        return cls._instance

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single string. Returns a 1D numpy array of shape (384,).
        """
        embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding.astype("float32")

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """
        Embeds a list of strings in one batch call (much faster than
        calling embed_text in a loop). Returns shape (N, 384).
        """
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        return embeddings.astype("float32")


# Module-level singleton instance — import and use directly
embedder = Embedder()