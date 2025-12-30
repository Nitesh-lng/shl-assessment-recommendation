import json
from pathlib import Path
from typing import Dict, List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

STRUCTURED_DATA_PATH = Path(
    "Data/final_enriched_data/shl_assessments_structured.json"
)

VECTOR_STORE_DIR = Path("Data/vector_store/shl_faiss")
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


def build_embedding_text(assessment: Dict) -> str:

    parts = []

    parts.append(f"Assessment Name: {assessment.get('name', '')}")


    job_profile = assessment.get("job_profile", {})
    if job_profile.get("job_levels"):
        parts.append("Job Levels: " + ", ".join(job_profile["job_levels"]))

    if job_profile.get("typical_roles"):
        parts.append("Typical Roles: " + ", ".join(job_profile["typical_roles"]))

    if job_profile.get("job_family"):
        parts.append(f"Job Family: {job_profile['job_family']}")

    
    meta = assessment.get("assessment_metadata", {})
    if meta.get("duration_minutes"):
        parts.append(f"Duration: {meta['duration_minutes']} minutes")

    if meta.get("test_types"):
        parts.append("Test Types: " + ", ".join(meta["test_types"]))

    
    skills = assessment.get("skills_competencies", [])
    if skills:
        parts.append("Skills & Competencies: " + " | ".join(skills))

    
    text_corpus = assessment.get("text_corpus", {})
    if text_corpus.get("description"):
        parts.append("Description: " + text_corpus["description"])

    if text_corpus.get("pdf_text"):
        parts.append("PDF Content: " + text_corpus["pdf_text"])

    return "\n".join(parts)


def create_documents(data: List[Dict]) -> List[Document]:
    documents = []

    for assessment in data:
        content = build_embedding_text(assessment)

        metadata = {
            "assessment_id": assessment["assessment_id"],
            "name": assessment["name"],
            "url": assessment.get("url"),
            "job_levels": assessment.get("job_profile", {}).get("job_levels", []),
            "duration_minutes": assessment.get("assessment_metadata", {}).get(
                "duration_minutes"
            ),
            "test_types": assessment.get("assessment_metadata", {}).get("test_types", []),
        }

        documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    return documents

def main():
    print("Loading structured assessment data...")
    with open(STRUCTURED_DATA_PATH, "r", encoding="utf-8") as f:
        assessments = json.load(f)

    print(f"Loaded {len(assessments)} assessments")

    print("Creating documents...")
    documents = create_documents(assessments)

    print(f"Created {len(documents)} documents")

    print("Generating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vector_store = FAISS.from_documents(documents, embeddings)

    print("Saving FAISS index...")
    vector_store.save_local(VECTOR_STORE_DIR)

    print("Vector store successfully built!")
    print(f"Location: {VECTOR_STORE_DIR}")


if __name__ == "__main__":
    main()
