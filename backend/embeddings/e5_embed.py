
from typing import List
from sentence_transformers import SentenceTransformer

_model = None
def _get():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "intfloat/e5-base",
            device="cpu",
            model_kwargs={"torch_dtype": "float32"}  # or torch.float32 if you import torch
        )
        # First dummy encode forces weights into memory
        #_model.encode(["warmup"], show_progress_bar=False)
    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    m = _get()
    return m.encode(texts, normalize_embeddings=True).tolist()
