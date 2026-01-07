
// frontend/src/components/RetrievedChunks.tsx
type Props = {
  citations: Array<{
    text: string;
    meta?: {
      url?: string;
      title?: string;
      strategy?: string;
      score?: string | number;
    };
  }>;
};

export default function RetrievedChunks({ citations }: Props) {
  if (!citations?.length) return null;

  return (
    <div>
      {citations.map((c, idx) => {
        const url = c.meta?.url;
        const title = c.meta?.title;
        const strategy = c.meta?.strategy;
        const score = c.meta?.score;

        return (
          <details key={idx} style={{ marginBottom: 8 }}>
            <summary>
              [{idx + 1}] {title || url || "Retrieved chunk"}
            </summary>
            {url && (
              <small style={{ display: "block", marginBottom: 6 }}>
                <a href={url} target="_blank" rel="noreferrer">
                  {url}
                </a>
              </small>
            )}
            <pre style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>{c.text}</pre>
            {(strategy || typeof score !== "undefined") && (
              <small style={{ color: "#555" }}>
                {strategy ? `strategy: ${strategy}` : ""}
                {strategy && typeof score !== "undefined" ? " • " : ""}
                {typeof score !== "undefined" ? `score: ${score}` : ""}
              </small>
            )}
          </details>
        );
      })}
    </div>
  );
}
