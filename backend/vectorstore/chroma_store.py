
import chromadb, os, pathlib
from chromadb.config import Settings

def get_chroma(persist_dir="data/index/chroma"):
    pathlib.Path(persist_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.Client(Settings(
        persist_directory=persist_dir,
        anonymized_telemetry=False
    ))
    return client

def upsert_docs(client, collection_name, items):
    col = client.get_or_create_collection(collection_name, metadata={"hnsw:space":"cosine"})
    ids = [f"{i['url']}#{k}" for k, i in enumerate(items)]
    texts = [i["chunk"] for i in items]
    metas = [{"url": i["url"], "title": i["title"], **i.get("meta",{})} for i in items]
    col.add(ids=ids, documents=texts, metadatas=metas)
    return col
