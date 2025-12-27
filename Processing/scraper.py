# Processing/scraper.py

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

RAW_DATA_DIR = Path("Data/Raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
