
import os
from typing import List, Optional
from openai import OpenAI, OpenAIError

_client = None

def init_client(api_key: Optional[str] = None):
    global _client
    # Priority: explicit argument → environment → error
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise OpenAIError(
            "OPENAI_API_KEY not set and no api_key passed to init_client()."
        )
    _client = OpenAI(api_key=key)
    return _client

def get_client():
    global _client
    if _client is None:
        # Lazy init from env if not initialized explicitly
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise OpenAIError("OPENAI_API_KEY missing; call init_client(api_key=...)")
        _client = OpenAI(api_key=key)
    return _client

def embed_texts(texts: List[str]) -> List[List[float]]:
    client = get_client()
    resp = client.embeddings.create(
        model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large"),
        input=texts
    )
    return [d.embedding for d in resp.data]
