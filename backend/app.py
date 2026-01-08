
import os
import sys
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import answer_queries 
import rag_index

load_dotenv()
app = FastAPI(title="ApplePay RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://apple-rag.vercel.app",        
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/build")
def build(embedder: str = "e5"):
    n = rag_index.build_index(embedder_name=embedder)
    return {"indexed_chunks": n}

@app.get("/search")
def search(q: str = Query(...), top_k: int = 6):
    ctx = answer_queries.retrieve(q, top_k=top_k)
    return {"results": ctx}

@app.get("/chat")
def chat(q: str = Query(...), top_k: int = 6):
    ctx = answer_queries.retrieve(q, top_k=top_k)
    result = answer_queries.answer(q, ctx)
    return result
