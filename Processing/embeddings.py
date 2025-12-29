import json
from pathlib import Path
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


STRUCTURED_DATA_PATH = Path("Data/final_enriched_data/shl_assessments_structured.json")
VECTOR_STORE_PATH = Path("Data/vector_store/shl_faiss")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


def build_embedding_text(assessment: Dict) -> str:

    parts = []

    parts.append(f"Assessment Name: {assessment.get('name', '')}")

    job_profile = assessment.get("job_profile", {})
    if job_profile:
        if job_profile.get("job_levels"):
            parts.append(
                "Job Levels: " + ", ".join(job_profile["job_levels"])
            )
        if job_profile.get("typical_roles"):
            parts.append(
                "Typical Roles: " + ", ".join(job_profile["typical_roles"])
            )
        if job_profile.get("job_family"):
            parts.append(
                f"Job Family: {job_profile['job_family']}"
            )

    description = assessment.get("text_corpus", {}).get("description")
    if description:
        parts.append(f"Description: {description}")

    skills = assessment.get("skills_competencies")
    if skills:
        parts.append(
            "Skills and Competencies: " + ", ".join(skills)
        )

    pdf_text = assessment.get("text_corpus", {}).get("pdf_text")
    if pdf_text:
        parts.append(f"Assessment Content: {pdf_text}")

    return "\n\n".join(parts)

def build_metadata(assessment: Dict) -> Dict:
    meta = {
        "assessment_id": assessment.get("assessment_id"),
        "name": assessment.get("name"),
        "url": assessment.get("url"),
        "languages": assessment.get("languages"),
    }

    assessment_meta = assessment.get("assessment_metadata", {})
    meta.update({
        "duration_minutes": assessment_meta.get("duration_minutes"),
        "remote_testing": assessment_meta.get("remote_testing"),
        "adaptive": assessment_meta.get("adaptive"),
        "test_types": assessment_meta.get("test_types"),
    })

    return meta

def build_vector_store():
    print("Loading structured assessment data...")
    with open(STRUCTURED_DATA_PATH, "r", encoding="utf-8") as f:
        assessments = json.load(f)

    print(f"Loaded {len(assessments)} assessments")

    documents: List[Document] = []

    for assessment in assessments:
        text = build_embedding_text(assessment)
        metadata = build_metadata(assessment)

        documents.append(
            Document(
                page_content=text,
                metadata=metadata
            )
        )

    print("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )

    print("Building FAISS vector store...")
    vector_store = FAISS.from_documents(
        documents,
        embedding=embeddings
    )

    VECTOR_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(VECTOR_STORE_PATH)

    print(f"Vector store saved at: {VECTOR_STORE_PATH}")


if __name__ == "__main__":
    build_vector_store()
