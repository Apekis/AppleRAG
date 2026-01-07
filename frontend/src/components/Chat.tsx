
// frontend/src/components/Chat.tsx
import { useState } from "react";
import { chat, search } from "../api";
import RetrievedChunks from "./RetrievedChunks";

type RetrievedChunk = {
  text: string;
  meta: {
    url?: string;
    title?: string;
    strategy?: string;
    score?: string | number;
  };
};

export default function Chat() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState<string>("");
  const [citations, setCitations] = useState<any[]>([]);
  const [latency, setLatency] = useState<number>(0);
  const [usage, setUsage] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [retrieved, setRetrieved] = useState<RetrievedChunk[]>([]);

  const onAsk = async () => {
    if (!q.trim()) return;
    setLoading(true);
    setErrorMsg("");
    setAnswer("");
    setCitations([]);
    setRetrieved([]);
    setLatency(0);
    setUsage(null);

    try {
      // Fire both requests in parallel
      const [chatRes, searchRes] = await Promise.all([chat(q, 3), search(q, 6)]);

      // Chat response (keep your existing shape)
      setAnswer(chatRes?.answer || "");
      setCitations(chatRes?.citations || []);
      setLatency(chatRes?.latency_ms ?? 0);
      setUsage(chatRes?.usage ?? null);

      // Search response provides top-k chunks
      setRetrieved(searchRes?.results || []);
    } catch (err: any) {
      setErrorMsg(err?.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  //linkify inline [1], [2] 
  const renderAnswerHtml = (s: string) =>
    s.replace(/\n/g, "<br/>"); // simple break conversion; expand as needed

  return (
    <div>
      <div className="row">
        <input
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Ask about Apple Pay (refunds, KYC, fees, security)..."
        />
        <button onClick={onAsk} disabled={loading || !q.trim()}>
          Ask
        </button>
      </div>

      {loading && <p>Thinking...</p>}
      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}

      {answer && (
        <div className="answer">
          <h3>Answer</h3>
          <div dangerouslySetInnerHTML={{ __html: renderAnswerHtml(answer) }} />
          <p>
            <b>Latency:</b> {latency} ms
          </p>
          {usage && (
            <p>
              <b>Tokens:</b> {usage.total_tokens} (prompt {usage.prompt_tokens}, completion{" "}
              {usage.completion_tokens})
            </p>
          )}

          {/* Optional Sources (if chat returns citations) */}
          {citations?.length > 0 && (
            <div className="sources">
              <h4>Sources</h4>
              <ol>
                {citations.map((c) => (
                  <li key={c.index}>
                    <a href={c.url} target="_blank" rel="noreferrer">
                      [{c.index}] {c.title || c.url}
                    </a>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      {/* Top‑k retrieved chunks directly under the answer */}
      {retrieved?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h3>Retrieved Context (Top {retrieved.length})</h3>
          <RetrievedChunks citations={retrieved} />
        </div>
      )}
    </div>
  );
}
