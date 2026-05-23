import hashlib
import os
from typing import Optional

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbeddingModel:
    _instance: Optional["EmbeddingModel"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.rag.embedding_model)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]

    def get_dimension(self) -> int:
        return settings.rag.embedding_dimension

    @staticmethod
    def generate_document_id(title: str, content: str) -> str:
        raw = "{}:{}".format(title, content[:200])
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()
