
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

    # # chunk
    # from chunking import chunkers

    # chunks = []
    # for d in pages:
    #     if chunk_strategy == "fixed":
    #         chunks += fixed_chunks(d, size=512, overlap=64)
    #     elif chunk_strategy == "semantic":
    #         chunks += semantic_chunks(d, threshold=0.75)
    #     elif chunk_strategy == "structural":
    #         chunks += structural_chunks(d)
    #     elif chunk_strategy == "recursive":
    #         chunks += recursive_chunks(d)
    #     elif chunk_strategy == "llm":
    #         chunks += llm_chunks(d)
    #     else:
    #         raise ValueError("unknown chunk strategy")

    # load chunks
    chunk_file="data/processed/semantic_chunks.json"
    with open(chunk_file,"r",encoding="utf-8") as f:
        chunks = json.load(f)

    # embed
    embed_fn = choose_embedder(embedder_name)
    vectors = embed_fn([c["chunk"] for c in chunks])

    # store
    if os.getenv("VECTOR_DB","chroma") == "chroma":
        client = get_chroma()
        col = upsert_docs(client, "applepay", chunks)
        # store embeddings in collection? chroma computes internally if using add with embeddings;
        # For clarity here, we rely on Chroma's default embed if configured, else we keep texts only.
        # You may switch to client with "add" including embeddings if needed.
    else:
        store = FaissStore(dim=len(vectors[0]))
        store.add(vectors, chunks)
        store.save()
    return len(chunks)

def retrieve(query: str, top_k: int = 6, embedder_name="openai"):
    embed_fn = choose_embedder(embedder_name)
    qv = embed_fn([query])[0]
    results = []
    if os.getenv("VECTOR_DB","chroma") == "chroma":
        client = get_chroma()
        col = client.get_or_create_collection("applepay")
        # Chroma similarity search (without re-embed)
        res = col.query(query_texts=[query], n_results=top_k)
        for i in range(len(res["documents"][0])):
            results.append({
                "text": res["documents"][0][i],
                "meta": res["metadatas"][0][i]
            })
    else:
        store = FaissStore(dim=len(qv))
        # load from disk (omitted for brevity — you can implement)
        # For now, this example assumes Chroma path.
        raise NotImplementedError("FAISS search loader not implemented in snippet")
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
