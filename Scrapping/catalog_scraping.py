import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import csv
import time
import os

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
START_STEP = 12 
MAX_PAGES = 32  
TYPE_INDIVIDUAL = 1
OUTPUT_JSON = "Data/Raw/shl_assessments.json"
OUTPUT_CSV = "Data/Raw/shl_assessments.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_catalog():
    all_assessments = []
    seen_urls = set()

    for page in range(MAX_PAGES):
        start = page * START_STEP
        url = f"{CATALOG_URL}?start={start}&type={TYPE_INDIVIDUAL}"

        print(f"Scraping: {url}")
        response = requests.get(url, headers=HEADERS, timeout=60)

        if response.status_code != 200:
            print("Failed to load page, stopping.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if not table:
            print("No table found, stopping.")
            break

        rows = table.find_all("tr")[1:]  
        if not rows:
            print("No rows found, stopping.")
            break

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            link = cols[0].find("a")
            if not link:
                continue

            name = link.get_text(strip=True)
            relative_url = link.get("href")
            full_url = urljoin(BASE_URL, relative_url)

            if full_url in seen_urls:
                continue

            seen_urls.add(full_url)

            remote_testing = "Yes" if cols[1].find("span", class_="-yes") else "No"

            adaptive_irt = "Yes" if cols[2].find("span", class_="-yes") else "No"

            test_keys = cols[3].find_all("span")
            test_type = ", ".join(k.get_text(strip=True) for k in test_keys) if test_keys else "N/A"

            all_assessments.append({
                "name": name,
                "url": full_url,
                "test_type": test_type,
                "remote_testing": remote_testing,
                "adaptive_irt": adaptive_irt
            })

        time.sleep(1)

    return all_assessments


def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(data, filename):
    if not data:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    print("Starting SHL catalog scraping...")

    assessments = scrape_catalog()

    print(f"\nTotal assessments collected: {len(assessments)}")

    save_json(assessments, OUTPUT_JSON)
    save_csv(assessments, OUTPUT_CSV)

    print(f"Saved JSON → {os.path.abspath(OUTPUT_JSON)}")
    print(f"Saved CSV  → {os.path.abspath(OUTPUT_CSV)}")
