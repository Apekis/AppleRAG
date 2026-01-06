#


import re, time, json, pathlib, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

APPLEPAY_ROOTS = [
    "https://www.apple.com/apple-pay/",
    "https://support.apple.com/apple-pay",
    "https://flutterwave.com/ke/support/payment-methods/apple-pay-frequently-asked-questions-faqs",
    "https://aibgb.co.uk/apple-pay/apple-pay-faqs",
    "https://www.americanexpress.com/us/credit-cards/features-benefits/digital-wallets/apple-pay/frequently-asked-questions.html",
    "https://www.wellsfargo.com/help/mobile-features/apple-pay-faqs/"
    #"https://horizonbank.com.au/help/faqs/apple-pay-faqs/" blocked
]

def get_links(base_url):
    resp = requests.get(base_url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"): continue
        full = urljoin(base_url, href)
        if "apple.com" in full and ("apple-pay" in full or "support.apple.com" in full):
            links.add(full)
    return sorted(links)

def fetch_page(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"\n{2,}", "\n", text).strip()
    title = soup.title.string.strip() if soup.title else ""
    return {"title": title, "text": text}

output_dir="data/raw"
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
visited = set()
pages = []
for root in APPLEPAY_ROOTS:
    links = get_links(root)
    for url in links:
        if url in visited: continue
        visited.add(url)
        try:
            html = fetch_page(url)
            cleaned = clean_text(html)
            pages.append({"url": url, **cleaned})
            time.sleep(0.5)
        except Exception as e:
            print("Failed:", url, e)
outpath = pathlib.Path(output_dir) / "bs4_pages.json"
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
print(f"BS4 scraped {len(pages)} pages → {outpath}")

#pages/sec 74/1m
#failures 1/7