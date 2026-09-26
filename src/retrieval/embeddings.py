from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from langchain_core.embeddings import Embeddings


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> Any:
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        pass

    try:
        # Use offline Chroma built-in ONNX implementation of all-MiniLM-L6-v2
        model = ONNXMiniLM_L6_V2()
        try:
            Path(model.DOWNLOAD_PATH).mkdir(parents=True, exist_ok=True)
        except OSError:
            model.DOWNLOAD_PATH = (
                Path(tempfile.gettempdir())
                / "day10-data-observability"
                / "chroma"
                / "onnx_models"
                / model.MODEL_NAME
            )
        return model
    except Exception:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model_name)


class MiniLMEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = _load_model(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if hasattr(self.model, "encode"):
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        raw_embeddings = self.model(texts)
        return [[float(x) for x in emb] for emb in raw_embeddings]

    def embed_query(self, text: str) -> list[float]:
        if hasattr(self.model, "encode"):
            embedding = self.model.encode([text], normalize_embeddings=True)
            return embedding[0].tolist()
        raw_embeddings = self.model([text])
        return [float(x) for x in raw_embeddings[0]]
