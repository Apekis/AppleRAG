
import json, pathlib

def normalize(in_files, out_file="data/processed/pages.json"):
    pathlib.Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in in_files:
        with open(f, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            for d in data:
                text = d.get("text")
                if not text and d.get("html"):
                    # crude HTML→text fallback
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(d["html"], "html.parser")
                    text = soup.get_text("\n")
                if not text: continue
                rows.append({
                    "url": d["url"],
                    "title": d.get("title",""),
                    "text": text.strip()
                })
    with open(out_file, "w", encoding="utf-8") as out:
        json.dump(rows, out, ensure_ascii=False, indent=2)
    print(f"Normalized {len(rows)} pages → {out_file}")

if __name__ == "__main__":
    normalize([
        "data/raw/bs4_pages.json",
        "data/raw/trafilatura_pages.json",
        # "data/raw/playwright_pages.json",
    ])
