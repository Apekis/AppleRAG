
"""
MiniLM embedding backend with batching and device control.

Default model: 'sentence-transformers/all-MiniLM-L6-v2' (768-dim)
Environment variables:
  MINILM_MODEL=sentence-transformers/all-MiniLM-L6-v2
  MINILM_DEVICE=cpu|cuda|cuda:0|cuda:1
  MINILM_BATCH=64
  MINILM_MAX_LEN=1024            # truncate long inputs to N tokens
  MINILM_NORMALIZE=true|false    # L2-normalize output vectors (default true)

Returned vectors are Python lists of floats, ready for FAISS or Chroma.
"""

import os
from typing import List, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("sentence-transformers is required: pip install sentence-transformers")

# Singleton model instance
_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    """Load the MiniLM model once (lazy singleton) with device from env."""
    global _model
    if _model is None:
        model_name = os.getenv("MINILM_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        device = os.getenv("MINILM_DEVICE", None)  # None => auto
        # SentenceTransformer accepts device="cpu", "cuda", or "cuda:0"
        _model = SentenceTransformer(model_name, device=device)
    return _model


def _normalize(v: np.ndarray) -> np.ndarray:
    """L2-normalize rows for cosine/IP similarity in FAISS."""
    norm = np.linalg.norm(v, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    return v / norm


def embed_texts(
    texts: List[str],
    batch_size: Optional[int] = None,
    max_len: Optional[int] = None,
    normalize: Optional[bool] = None,
) -> List[List[float]]:
    """
    Embed a list of texts using MiniLM with batching and optional truncation/normalization.

    Args:
        texts: list of strings
        batch_size: override batch size (default from env MINILM_BATCH=64)
        max_len: truncate each input to at most this many tokens (env MINILM_MAX_LEN=1024)
        normalize: L2-normalize output vectors (env MINILM_NORMALIZE=true)

    Returns:
        List of embedding vectors (list[float])
    """
    model = _get_model()

    # Default configuration from env
    bs = int(os.getenv("MINILM_BATCH", "64")) if batch_size is None else int(batch_size)
    max_len = int(os.getenv("MINILM_MAX_LEN", "1024")) if max_len is None else int(max_len)
    norm_flag = os.getenv("MINILM_NORMALIZE", "true").lower() in ("1", "true", "yes") if normalize is None else bool(normalize)

    # Optional truncation (model uses its own tokenizer)
    # The model's encode() supports 'truncate_dim' indirectly via tokenizer settings; we pre-truncate naïvely to reduce length
    # using simple whitespace split to avoid extremely long inputs. For stricter control, consider using model.tokenize.
    if max_len and max_len > 0:
        prepped = [(" ".join(t.split()[:max_len])) if t else "" for t in texts]
    else:
        prepped = texts

    # Encode in batches; convert to numpy
    vecs = model.encode(
        prepped,
        batch_size=bs,
        convert_to_numpy=True,
        normalize_embeddings=False,  # we control normalization ourselves
        show_progress_bar=False,
    )

    if norm_flag:
        vecs = _normalize(vecs)

    # Return Python lists
    return [v.tolist() for v in vecs]
