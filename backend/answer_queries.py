
from typing import Dict, List, Tuple
from openai import OpenAI
import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embeddings.e5_embed import embed_texts as e5_embed
from embeddings.bge_embed import embed_texts as bge_embed
import time
import json


def retrieve(query: str, top_k: int = 6):
    embed_fn = e5_embed
    qv = embed_fn([query])[0]
    results = []

    # FAISS retrieval
    indexfile="index.faiss"
    docsfile="docs.json"
    # index_dir = "../data/index/faiss"
    # index_path = os.path.join(index_dir, indexfile)
    # docs_path = os.path.join(index_dir, docsfile)

    if not os.path.exists(indexfile) or not os.path.exists(docsfile):
        raise FileNotFoundError("FAISS index or docs.json not found. Run build_index first.")

    # Load FAISS index
    import faiss
    import numpy as np
    with open(docsfile, "r", encoding="utf-8") as f:
        docs = json.load(f)

    index = faiss.read_index(indexfile)
    q = np.array([qv]).astype("float32")
    faiss.normalize_L2(q)
    D, I = index.search(q, top_k)

    for rank, idx in enumerate(I[0]):
        doc = docs[idx]
        results.append({
            "text": doc.get("chunk", doc.get("chunk_text", "")),
            "meta": {
                "url": doc.get("url"),
                "title": doc.get("title"),
                "strategy": doc.get("strategy", "unknown"),
                "score": float(D[0][rank])
            }
        })
    return results


def answer(query: str, contexts: List[Dict]) -> Dict:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    sys = "You are a customer support assistant for Apple Pay. Answer strictly using the provided context and cite sources."
    citations_md = "\n\n".join([f"[{i+1}] {c['meta']['title'] or c['meta']['url']} — {c['meta']['url']}" for i, c in enumerate(contexts)])
    context_text = "\n\n---\n\n".join([c["text"] for c in contexts])

    prompt = f"""Question: {query}

Context (use only this information):
{context_text}

Citations:
{citations_md}

Instructions:
- If an answer is not present in the context, say you don't know and suggest contacting Apple support.
- Include bracketed citation numbers like [1], [2] inline where relevant.
- Keep answers concise and accurate."""

    t0 = time.time()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL","gpt-4o-mini"),
        messages=[{"role":"system","content":sys},
                  {"role":"user","content":prompt}],
        temperature=0.0
    )
    dt = int((time.time() - t0) * 1000)
    content = resp.choices[0].message.content
    usage = resp.usage
    return {
        "answer": content,
        "citations": [{"index": i+1, "url": c["meta"]["url"], "title": c["meta"]["title"], "snippet": c["text"][:240]} for i, c in enumerate(contexts)],
        "latency_ms": dt,
        "usage": {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens, "total_tokens": usage.total_tokens}
    }

#e5_embed: 18.9MB, Latency P50: 2315.5 ms; P95: 6044 ms
#bge: 9.4MB
#minilim: 9.4MB
