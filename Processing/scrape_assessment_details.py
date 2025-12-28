import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import re

INPUT_PATH = Path("Data/Raw/shl_product_urls.json")
OUTPUT_PATH = Path("Data/Enriched/shl_assessments_enriched.json")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_assessment(url):
    r = requests.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    def text_after(label):
        h = soup.find("strong", string=re.compile(label, re.I))
        return clean(h.parent.get_text()) if h else None

    return {
        "name": clean(soup.find("h1").get_text()),
        "url": url,
        "job_levels": text_after("Job levels"),
        "languages": text_after("Languages"),
        "assessment_length_minutes": text_after("Approximate Completion Time"),
        "remote_testing": "Yes" in soup.get_text(),
        "adaptive_irt": "Adaptive" in soup.get_text(),
        "description": clean(
            soup.find("div", class_="description").get_text()
        ) if soup.find("div", class_="description") else None,
        "pdf_url": (
            soup.find("a", href=re.compile("Fact Sheet"))["href"]
            if soup.find("a", href=re.compile("Fact Sheet"))
            else None
        )
    }

def run():
    with open(INPUT_PATH, "r") as f:
        urls = json.load(f)

    data = []
    for item in urls:
        try:
            data.append(scrape_assessment(item["url"]))
        except Exception as e:
            print("Failed:", item["url"], e)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Enriched {len(data)} assessments")

if __name__ == "__main__":
    run()
