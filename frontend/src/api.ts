
// frontend/src/api.ts
import ky from "ky";

const API = ky.create({
  prefixUrl: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const chat = async (q: string, top_k = 6) =>
  API.get("chat", { searchParams: { q, top_k } }).json<any>();

export const search = async (q: string, top_k = 6) =>
  API.get("search", { searchParams: { q, top_k } }).json<any>();

export const build = async (embedder = "e5") =>
  API.post("build", { searchParams: {embedder } }).json<any>();
