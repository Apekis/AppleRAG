#emdedings
from backend.embeddings.e5_embed import embed_texts as e5_embed
from backend.embeddings.bge_embed import embed_texts as bge_embed
from backend.vectorstore.chroma_store import get_chroma, upsert_docs
from backend.embeddings.minilm_embed import embed_texts as minilm_embed
from backend.vectorstore.faiss_store import FaissStore
import faiss

import json
import os
import pandas as pd
import numpy as np

# load chunks
chunk_file="data/chunks/llm_chunks.json"
with open(chunk_file,"r",encoding="utf-8") as f:
    chunks = json.load(f)

#embed

embed_fn = e5_embed
vectors_e5 = embed_fn([c["chunk"] for c in chunks])
# Save embeddings to file
embeddings_df = pd.DataFrame(vectors_e5)
embeddings_df_save_path = "vectors_e5.csv"
embeddings_df.to_csv(embeddings_df_save_path, index=False)
vectors=vectors_e5
indexfile="index_e5.faiss"
docsfile="docs_e5.json"

# embed_fn = bge_embed
# vectors_bge = embed_fn([c["chunk"] for c in chunks])
# # Save embeddings to file
# embeddings_df = pd.DataFrame(vectors_bge)
# embeddings_df_save_path = "vectors_bge.csv"
# embeddings_df.to_csv(embeddings_df_save_path, index=False)
# vectors=vectors_bge
# indexfile="index_bge.faiss"
# docsfile="docs_e5.json"

# embed_fn = minilm_embed
# vectors_minilm = embed_fn([c["chunk"] for c in chunks])
# # Save embeddings to file
# embeddings_df = pd.DataFrame(vectors_minilm)
# embeddings_df_save_path = "vectors_minilm.csv"
# embeddings_df.to_csv(embeddings_df_save_path, index=False)
# vectors=vectors_minilm
# indexfile="index_minilm.faiss"
# docsfile="docs_minilm.json"

#store

index_dir = "data/index/faiss"
os.makedirs(index_dir, exist_ok=True)

dim = len(vectors[0])
index = faiss.IndexFlatIP(dim)  # cosine similarity with normalized vectors
emb = np.array(vectors).astype("float32")
faiss.normalize_L2(emb)
index.add(emb)

# Save index
faiss.write_index(index, os.path.join(index_dir, indexfile))

# Save docs metadata
docs_path = os.path.join(index_dir, docsfile)
with open(docs_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"✅ FAISS index built with {len(chunks)} chunks → {index_dir}")
