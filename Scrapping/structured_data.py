import json
import os
import re
from urllib.parse import urlparse

INPUT_FILE = "Data/Enriched/shl_assessments_enriched.json"
OUTPUT_DIR = "Data/final_enriched_data/final_enriched_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "shl_assessments_structured.json")


def slugify(text):
    return text.lower().replace(" ", "-").replace(",", "")


def parse_test_types(test_type_str):
    return [t.strip() for t in test_type_str.split(",")] if test_type_str else []


def extract_competencies(pdf_text):
    """
    Extract high-signal competencies from PDF text.
    Simple but effective rule-based approach.
    """
    if not pdf_text:
        return []

    competencies = []
    pattern = re.compile(r"([A-Z][A-Za-z\s&]+):\s")

    for match in pattern.finditer(pdf_text):
        name = match.group(1).strip()
        if len(name) < 3:
            continue
        competencies.append(name)

    seen = set()
    final = []
    for c in competencies:
        if c not in seen:
            seen.add(c)
            final.append(c)

    return final


def extract_job_family(pdf_text):
    if not pdf_text:
        return None
    match = re.search(r"Job Family/Title\s+([A-Za-z\s]+)", pdf_text)
    return match.group(1).strip() if match else None


def extract_roles(description):
    if not description:
        return []

    roles_match = re.search(
        r"Potential job titles.*?are:(.+?)\.",
        description,
        re.IGNORECASE,
    )
    if not roles_match:
        return []

    roles = roles_match.group(1)
    return [r.strip() for r in roles.split(",")]


def build_structured_record(item):
    assessment_id = slugify(item["name"])

    job_levels_raw = item.get("job_levels") or ""
    languages_raw = item.get("languages") or ""

    structured = {
        "assessment_id": assessment_id,
        "name": item["name"],
        "url": item["url"],

        "job_profile": {
            "job_levels": [
                jl.strip()
                for jl in job_levels_raw.split(",")
                if jl.strip()
            ],
            "job_family": extract_job_family(item.get("pdf_text")),
            "typical_roles": extract_roles(item.get("description")),
        },

        "assessment_metadata": {
            "duration_minutes": item.get("assessment_length_minutes"),
            "remote_testing": item.get("remote_testing") == "Yes",
            "adaptive": item.get("adaptive_irt") == "Yes",
            "test_types": parse_test_types(item.get("test_type")),
        },

        "languages": [
            lang.strip()
            for lang in languages_raw.split(",")
            if lang.strip()
        ],

        "skills_competencies": extract_competencies(item.get("pdf_text")),

        "text_corpus": {
            "description": item.get("description"),
            "pdf_text": item.get("pdf_text"),
        },
    }

    return structured



def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        enriched_data = json.load(f)

    structured_data = []

    for item in enriched_data:
        structured_data.append(build_structured_record(item))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)

    print(f"Structured data created: {OUTPUT_FILE}")
    print(f"Total records: {len(structured_data)}")


if __name__ == "__main__":
    main()
