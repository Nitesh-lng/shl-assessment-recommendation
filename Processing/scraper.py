"""
scraper.py

Responsible for:
- Fetching SHL product catalogue pages
- Extracting raw assessment information
- Saving raw outputs for downstream processing
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict

RAW_DATA_DIR = Path("Data/Raw/shl_product_pages")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_assessment_page(url: str) -> str:
    """Fetch raw HTML of an assessment page"""
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def parse_assessment_page(html: str) -> Dict:
    """Parse assessment details from HTML"""
    soup = BeautifulSoup(html, "html.parser")

    # TODO: implement parsing logic
    return {}


def save_raw_assessment(data: Dict, assessment_id: str):
    """Save parsed assessment data"""
    output_path = RAW_DATA_DIR / f"{assessment_id}.json"
    # TODO: save json
