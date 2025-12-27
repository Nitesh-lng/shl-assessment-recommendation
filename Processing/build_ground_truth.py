import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse

RAW_DATA_PATH = Path("Data/Raw/Gen_AI Dataset.xlsx")
OUTPUT_PATH = Path("Data/evaluation/ground_truth.json")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def extract_assessment_id(url: str) -> str:
    """
    Extracts assessment slug from SHL product URL
    """
    path = urlparse(url).path
    return path.rstrip("/").split("/")[-1]

def build_ground_truth():
    df = pd.read_excel(RAW_DATA_PATH)

    grouped = defaultdict(set)

    for _, row in df.iterrows():
        query = row["Query"].strip()
        assessment_id = extract_assessment_id(row["Assessment_url"])
        grouped[query].add(assessment_id)

    ground_truth = []

    for query, assessments in grouped.items():
        ground_truth.append({
            "query": query,
            "ground_truth_assessment_ids": sorted(list(assessments))
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    print(f"✅ Saved {len(ground_truth)} evaluation queries → {OUTPUT_PATH}")

if __name__ == "__main__":
    build_ground_truth()
