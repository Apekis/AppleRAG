
import trafilatura

URLS = [
    "https://www.apple.com/apple-pay/",
    "https://support.apple.com/apple-pay",
    "https://flutterwave.com/ke/support/payment-methods/apple-pay-frequently-asked-questions-faqs",
    "https://aibgb.co.uk/apple-pay/apple-pay-faqs",
    "https://www.americanexpress.com/us/credit-cards/features-benefits/digital-wallets/apple-pay/frequently-asked-questions.html",
    "https://www.wellsfargo.com/help/mobile-features/apple-pay-faqs/"
    "https://horizonbank.com.au/help/faqs/apple-pay-faqs/"
]

output_dir="data/raw"
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
pages = []
for url in URLS:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        print("Fail:", url); continue
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    pages.append({"url": url, "title": "", "text": text or ""})
outpath = pathlib.Path(output_dir) / "trafilatura_pages.json"
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
print(f"Trafilatura scraped {len(pages)} pages → {outpath}")

#pages/sec: 5/4s
#failure:1/7
