import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pypdf import PdfReader
import io
import re
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


INPUT_FILE = "Data/Raw/shl_assessments.json"
OUTPUT_FILE = "Data/Enriched/shl_assessments_enriched.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 30
SLEEP_SECONDS = 1


def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session


session = create_session()


def extract_pdf_text(pdf_url):
    try:
        r = session.get(pdf_url, timeout=TIMEOUT)
        r.raise_for_status()

        reader = PdfReader(io.BytesIO(r.content))
        text = ""

        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

        return text.strip()

    except Exception as e:
        print(f"⚠️ PDF failed: {pdf_url}")
        return None


def clean_page_text(soup):
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator="\n")

def scrape_detail(url):
    try:
        print(f"Scraping: {url}")

        r = session.get(url, timeout=TIMEOUT)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")
        page_text = clean_page_text(soup)

        description = None
        desc_match = re.search(
            r"Description\s*(.+?)Job levels",
            page_text,
            re.IGNORECASE | re.DOTALL,
        )
        if desc_match:
            description = desc_match.group(1).strip()

        job_levels = None
        jl_match = re.search(r"Job levels\s*(.+)", page_text, re.IGNORECASE)
        if jl_match:
            job_levels = jl_match.group(1).strip()

        languages = None
        lang_match = re.search(r"Languages\s*(.+)", page_text, re.IGNORECASE)
        if lang_match:
            languages = lang_match.group(1).strip()

        duration = None
        dur_match = re.search(
            r"Approximate Completion Time.*?(\d+)",
            page_text,
            re.IGNORECASE,
        )
        if dur_match:
            duration = int(dur_match.group(1))

        pdf_url = None
        pdf_link = soup.find("a", string=re.compile("Product Flyer|Fact Sheet", re.I))
        if pdf_link and pdf_link.get("href"):
            pdf_url = urljoin(url, pdf_link["href"])

        pdf_text = extract_pdf_text(pdf_url) if pdf_url else None

        return {
            "description": description,
            "job_levels": job_levels,
            "languages": languages,
            "assessment_length_minutes": duration,
            "pdf_url": pdf_url,
            "pdf_text": pdf_text,
        }

    except Exception as e:
        print(f"Failed page (skipped): {url}")
        return {
            "description": None,
            "job_levels": None,
            "languages": None,
            "assessment_length_minutes": None,
            "pdf_url": None,
            "pdf_text": None,
        }

def main():
    os.makedirs("Data/Enriched", exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        assessments = json.load(f)

    enriched = []

    for idx, item in enumerate(assessments, start=1):
        print(f"\n[{idx}/{len(assessments)}]")
        details = scrape_detail(item["url"])
        enriched.append({**item, **details})
        time.sleep(SLEEP_SECONDS)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\nDONE → {OUTPUT_FILE}")
    print(f"Total processed: {len(enriched)}")


if __name__ == "__main__":
    main()
