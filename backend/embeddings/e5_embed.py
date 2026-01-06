
from typing import List
from sentence_transformers import SentenceTransformer

_model = None
def _get():
    global _model
    if _model is None:
        _model = SentenceTransformer("intfloat/e5-base")
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    m = _get()
    return m.encode(texts, normalize_embeddings=True).tolist()
