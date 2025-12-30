from pathlib import Path
from typing import List, Dict
from collections import defaultdict

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

VECTOR_STORE_PATH = Path("Data/vector_store/shl_faiss")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

TOP_K = 15
FETCH_K = 40
LAMBDA_MULT = 0.6

def load_vector_store() -> FAISS:
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME
    )

    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

def get_mmr_retriever(vector_store: FAISS):
    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": TOP_K,
            "fetch_k": FETCH_K,
            "lambda_mult": LAMBDA_MULT
        }
    )

def aggregate_chunks_to_assessments(
    docs: List[Document],
    top_n: int = 5
) -> List[Dict]:

    grouped = defaultdict(lambda: {
        "score": 0.0,
        "count": 0,
        "metadata": None,
        "evidence": []
    })

    for doc in docs:
        meta = doc.metadata
        aid = meta.get("assessment_id")

        if not aid:
            continue

        grouped[aid]["score"] += doc.metadata.get("score", 1.0)
        grouped[aid]["count"] += 1
        grouped[aid]["metadata"] = meta
        grouped[aid]["evidence"].append(doc.page_content)

    results = []

    for aid, data in grouped.items():
        meta = data["metadata"]

        results.append({
            "assessment_id": aid,
            "name": meta.get("name"),
            "url": meta.get("url"),

            "job_levels": meta.get("job_levels"),
            "job_family": meta.get("job_family"),
            "typical_roles": meta.get("typical_roles"),

            "test_types": meta.get("test_types"),
            "duration_minutes": meta.get("duration_minutes"),
            "remote_testing": meta.get("remote_testing"),

            "match_score": round(data["score"], 3),
            "supporting_chunks": data["count"],
            "evidence": data["evidence"][:3] 
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return results[:top_n]


# Manual test

'''if __name__ == "__main__":
    vs = load_vector_store()
    retriever = get_mmr_retriever(vs)

    query = "Python developer with 4 years experience in AI automation"
    docs = retriever.invoke(query)

    print(f"Retrieved chunks: {len(docs)}")
    print("Sample metadata:", docs[0].metadata)

    recs = aggregate_chunks_to_assessments(docs, top_n=5)

    print("\nTop Recommendations:\n")
    for r in recs:
        print(r["assessment_id"], "→ score:", r["match_score"])
'''