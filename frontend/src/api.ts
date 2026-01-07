
// frontend/src/api.ts
import ky from "ky";

const API = ky.create({
  prefixUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const chat = async (q: string, top_k = 6) =>
  API.get("chat", { searchParams: { q, top_k } }).json<any>();

// NEW: search endpoint to fetch retrieved chunks
export const search = async (q: string, top_k = 6) =>
  API.get("search", { searchParams: { q, top_k } }).json<any>();

export const build = async (chunk_strategy = "recursive", embedder = "openai") =>
  API.post("build", { searchParams: { chunk_strategy, embedder } }).json<any>();
