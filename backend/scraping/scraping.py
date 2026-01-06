
def load_pages(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def count_tokens(text):
    # Simple token count by whitespace split
    return len(text.split())

def noise_ratio(text):
    # Heuristic: ratio of non-alphanumeric characters to total characters
    if not text:
        return 1.0
    non_alpha = len(re.findall(r"[^a-zA-Z0-9\s]", text))
    return round(non_alpha / len(text), 4)

def report(method_name, pages):
    num_pages = len(pages)
    total_tokens = 0
    noise_scores = []
    for p in pages:
        txt = p.get("text", "")
        total_tokens += count_tokens(txt)
        noise_scores.append(noise_ratio(txt))
    avg_noise = round(sum(noise_scores) / len(noise_scores), 4) if noise_scores else 0
    return {
        "method": method_name,
        "#pages": num_pages,
        "#tokens": total_tokens,
        "avg_noise_ratio": avg_noise
    }

base_dir = pathlib.Path("data/raw")
bs4_file = base_dir / "bs4_pages.json"
tra_file = base_dir / "trafilatura_pages.json"

bs4_pages = load_pages(bs4_file)
tra_pages = load_pages(tra_file)

bs4_report = report("BeautifulSoup", bs4_pages)
tra_report = report("Trafilatura", tra_pages)

print("\n=== Scrape Quality Report ===")
for r in [bs4_report, tra_report]:
    print(f"\nMethod: {r['method']}")
    print(f"Pages: {r['#pages']}")
    print(f"Tokens: {r['#tokens']}")
    print(f"Avg Noise Ratio: {r['avg_noise_ratio']}")

# Optional: Save to JSON
out_path = base_dir / "scrape_quality_report.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"BeautifulSoup": bs4_report, "Trafilatura": tra_report}, f, indent=2)
print(f"\nReport saved to {out_path}")


# === Scrape Quality Report ===

# Method: BeautifulSoup
# Pages: 74
# Tokens: 295217
# Avg Noise Ratio: 0.0695

# Method: Trafilatura
# Pages: 5
# Tokens: 4493
# Avg Noise Ratio: 0.0281
