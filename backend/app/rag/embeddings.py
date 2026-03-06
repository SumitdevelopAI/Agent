from sentence_transformers import SentenceTransformer
import torch
from typing import List
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

_device = "cuda" if torch.cuda.is_available() else "cpu"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME, device=_device)
    return _model


def embed_text(text: str) -> List[float]:
    """
    Embed single text string.
    Returns normalized embedding vector.
    """

    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embedding.tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Embed list of texts efficiently.
    """

    model = get_model()

    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    return embeddings.tolist()