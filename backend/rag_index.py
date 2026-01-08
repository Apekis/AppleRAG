
import os, json, time
from typing import Dict, List, Tuple
from dotenv import load_dotenv
load_dotenv()

from embeddings.openai_embed import embed_texts as openai_embed
from embeddings.e5_embed import embed_texts as e5_embed
from embeddings.bge_embed import embed_texts as bge_embed
from vectorstore.chroma_store import get_chroma, upsert_docs
from vectorstore.faiss_store import FaissStore
from openai import OpenAI

def choose_embedder(name: str):
    if name.lower() == "openai":
        return openai_embed
    if name.lower() == "e5":
        return e5_embed
    if name.lower() == "bge":
        return bge_embed
    raise ValueError("Unknown embedder")

def build_index(pages_path="data/processed/pages.json",
                chunk_strategy="recursive",
                embedder_name="openai"):
    # load pages
    with open(pages_path,"r",encoding="utf-8") as f:
        pages = json.load(f)

    # load chunks
    chunk_file="data/processed/semantic_chunks.json"
    with open(chunk_file,"r",encoding="utf-8") as f:
        chunks = json.load(f)

    # embed
    embed_fn = choose_embedder(embedder_name)
    vectors = embed_fn([c["chunk"] for c in chunks])

    # store
    store = FaissStore(dim=len(vectors[0]))
    store.add(vectors, chunks)
    store.save()
    return len(chunks)

