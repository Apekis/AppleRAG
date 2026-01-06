

from pathlib import Path
import json

# Paths
INPUT_FILE = "data/processed/pages.json"
OUTPUT_DIR = Path("data/chunks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_pages(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def chunk_page(page, strategy="fixed", **kwargs):
    text = page.get("text", "")
    if not text.strip():
        return []
    if strategy == "fixed":
        chunks = fixed_chunk_text(text, chunk_size=kwargs.get("chunk_size", 512),overlap=kwargs.get("overlap", 64))
    elif strategy == "semantic":
        chunks = semantic_chunk_text(text,
                                     similarity_threshold=kwargs.get("similarity_threshold", 0.8),
                                     max_tokens=kwargs.get("max_tokens", 500))
    elif strategy == "recursive":
        chunks = recursive_chunk_text(text,
                                      max_chunk_size=kwargs.get("max_chunk_size", 1000))
    elif strategy == "structure":
        chunks = structure_chunk_text(text)
    elif strategy == "llm":
        chunks = llm_chunk_text(text,
                                chunk_size=kwargs.get("chunk_size", 1000),
                                model=kwargs.get("model", "gpt-4o-mini"),
                                api_key=kwargs.get("api_key"))
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    # Wrap chunks with metadata
    return [
        {
            "url": page.get("url"),
            "title": page.get("title"),
            "chunk_index": i,
            "chunk": c,
            "chunk_char_count": len(c),
            "chunk_word_count": len(c.split()),
            "chunk_token_count": round(len(c) / 4, 2),  # approx tokens
            "strategy": strategy
        }
        for i, c in enumerate(chunks)
    ]

def process_pages(strategy="fixed", **kwargs):
    pages = load_pages(INPUT_FILE)
    all_chunks = []
    for page in pages:
        all_chunks.extend(chunk_page(page, strategy=strategy, **kwargs))
    # Save chunks
    out_file = OUTPUT_DIR / f"{strategy}_chunks.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"✅ {strategy.capitalize()} chunking complete: {len(all_chunks)} chunks saved to {out_file}")

# Example runs:
process_pages(strategy="fixed", chunk_size=512, overlap=128)
process_pages(strategy="semantic", similarity_threshold=0.75, max_tokens=500)
process_pages(strategy="recursive", max_chunk_size=800)
process_pages(strategy="structure")
process_pages(strategy="llm", chunk_size=800, model="gpt-4o-mini", api_key="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")

#chunk sizes
#Fixed chunking complete: 9725 chunks saved to data\chunks\fixed_chunks.json  2s
#Llm chunking complete: 5996 chunks saved to data\chunks\llm_chunks.json 43m
#semantic 6539  21m
#recursive: 55213 
#structure: 365 
#fixed size: 256,0: 1209, 256,64: 1598, 256,128: 2380,
#  512,0: 631, 512,64: 712, 512,128: 816,