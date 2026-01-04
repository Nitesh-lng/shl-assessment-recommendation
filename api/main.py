from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from typing import Optional
from Processing.retrievel import (
    load_vector_store,
    get_mmr_retriever,
    aggregate_chunks_to_assessments,
)


app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="Semantic recommendation engine for SHL assessments using FAISS + MMR",
    version="1.0.0",
)

vector_store = load_vector_store()
retriever = get_mmr_retriever(vector_store)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class AssessmentResponse(BaseModel):
    assessment_id: str
    name: str
    match_score: float
    job_levels: List[str]
    test_types: List[str]
    duration_minutes: Optional[int] = None

@app.get("/")
def health_check():
    return {"status": "API is running"}


@app.post("/recommend", response_model=List[AssessmentResponse])
def recommend_assessments(payload: QueryRequest):

    docs = retriever.invoke(payload.query)

    results = aggregate_chunks_to_assessments(
    docs,
    top_n=payload.top_k
)


    response = []
    for r in results:
        response.append({
            "assessment_id": r.get("assessment_id", ""),
            "name": r.get("name", ""),
            "match_score": float(r.get("match_score", 0.0)),
            "job_levels": r.get("job_levels", []),
            "test_types": r.get("test_types", []),
            "duration_minutes": r.get("duration_minutes", 0),
        })

    return response

