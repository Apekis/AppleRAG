
import faiss, numpy as np, json, pathlib

class FaissStore:
    def __init__(self, dim, index_dir="data/index/faiss"):
        self.index_dir = pathlib.Path(index_dir); self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index = faiss.IndexFlatIP(dim)  # cosine with normalized vectors
        self.docs = []

    def add(self, embeddings, items):
        emb = np.array(embeddings).astype("float32")
        # normalize
        faiss.normalize_L2(emb)
        self.index.add(emb)
        self.docs.extend(items)

    def search(self, query_emb, k=6):
        q = np.array([query_emb]).astype("float32")
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        return [(D[0][i], self.docs[idx]) for i, idx in enumerate(I[0])]

    def save(self):
        faiss.write_index(self.index, str(self.index_dir / "index.faiss"))
        with open(self.index_dir / "docs.json","w") as f:
            json.dump(self.docs, f, ensure_ascii=False, indent=2)
