# SHL Assessment Recommendation Engine 

An **AI-powered assessment recommendation system** that suggests the most relevant **SHL assessments** for a given hiring requirement using **semantic search, embeddings, FAISS, and MMR-based retrieval**.

This project demonstrates an **end-to-end GenAI / RAG-style pipeline** — from **raw unstructured data ingestion** to **structured knowledge creation**, **vector search**, **evaluation**, and **production-ready APIs + UI**.

---

## Problem Statement

Hiring teams often struggle to select the **right assessments** from a large catalog based on a job description.

### Example Query:
> *"Python developer with 4 years of experience in AI automation"*

### Objective:
Automatically recommend the **most relevant SHL assessments**, ranked by **semantic relevance and diversity**.

---

## Solution Overview

This system uses:

- **Sentence embeddings** for semantic understanding
- **FAISS vector database** for fast similarity search
- **MMR (Maximal Marginal Relevance)** for balanced and diverse results
- **FastAPI** as backend inference service
- **Streamlit** as interactive frontend

---

## System Architecture

```

```
              ┌────────────────────────────┐
              │     Raw SHL Data Sources    │
              │   (CSV / JSON / PDFs)       │
              └─────────────┬──────────────┘
                            │
                            ▼
    ┌──────────────────────────────────────────┐
    │   Data Structuring & Enrichment           │
    │   - Cleaning                              │
    │   - Normalization                         │
    │   - Metadata extraction                   │
    └─────────────┬────────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────────┐
    │   Structured Assessment JSON              │
    │   (ML-ready canonical schema)             │
    └─────────────┬────────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────────┐
    │   Embedding Generation                    │
    │   - SentenceTransformers                  │
    │   - Dense vector representation           │
    └─────────────┬────────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────────────┐
    │   FAISS Vector Store                      │
    │   - Similarity search                     │
    │   - MMR-based retrieval                   │
    └─────────────┬────────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  FastAPI Backend   │
        │  /recommend API    │
        └─────────┬─────────┘
                  │
                  ▼
    ┌──────────────────────────────────────────┐
    │   Streamlit Frontend                      │
    │   Interactive Recommendation UI           │
    └──────────────────────────────────────────┘
```

```

---

## Project Structure

```

shl-assessment-recommendation/
│
├── API/
│   └── main.py                     # FastAPI application
│
├── Processing/
│   ├── scraper_assessment_details.py
│   ├── data_structuring.py         # Raw → structured
│   ├── embeddings.py               # Embedding generation
│   ├── vector_store.py             # FAISS store logic
│   ├── retrieval.py                # MMR retrieval
│   └── evaluation.py               # Recall@K, MRR
│
├── Data/
│   ├── Raw/                        # Unstructured data
│   ├── Enriched/                   # Cleaned data
│   ├── final_enriched_data/        # Structured JSON
│   ├── vector_store/               # FAISS index
│   └── evaluation/
│       └── ground_truth.json
│
├── Frontend/
│   └── app.py                      # Streamlit UI
│
├── requirements.txt
├── runtime.txt
└── README.md

````

---

## Data Transformation Pipeline  
### Unstructured → Structured → Searchable

### Raw Data (Unstructured)

Sources:
- CSV files
- JSON dumps
- PDFs from SHL catalog

Problems:
- Inconsistent fields
- Missing metadata
- Non-ML-ready formats

Example:
```json
{
  "title": "Python (New)",
  "desc": "Test for Python developers...",
  "duration": "60 mins"
}
````

---

### Data Structuring & Enrichment

Raw data is normalized into a **canonical schema**:

```json
{
  "assessment_id": "python-new",
  "name": "Python (New)",
  "description": "Assessment for Python developers",
  "job_levels": ["Mid-Professional"],
  "test_types": ["K"],
  "duration_minutes": 60,
  "skills": ["Python", "Programming"]
}
```

✅ Clean
✅ Normalized
✅ Consistent
✅ ML-ready

---

### Embedding Generation

Each assessment is converted into a **dense semantic vector** using:

* `sentence-transformers`
* Combined textual fields:

  * Name
  * Description
  * Skills
  * Job levels

```
Text → High-dimensional embedding
```

---

### Vector Store (FAISS)

* All embeddings stored in **FAISS**
* Enables **fast semantic similarity search**
* Supports **MMR-based retrieval**

---

## Retrieval Strategy (MMR)

Instead of returning only the closest vectors, we apply:

**Maximal Marginal Relevance (MMR)**

This ensures:

* High relevance
* Reduced redundancy
* Better diversity

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": top_k, "lambda_mult": 0.5}
)
```

---

## Evaluation

Evaluation metrics used:

* **Recall@5**
* **Recall@10**
* **MRR (Mean Reciprocal Rank)**

Example results:

```
Recall@5  = 0.20
Recall@10 = 0.30
MRR       = 0.17
```

---

## API (FastAPI)

### Endpoint

```
POST /recommend
```

### Request

```json
{
  "query": "Python developer with 4 years experience in AI automation",
  "top_k": 5
}
```

### Response

```json
[
  {
    "assessment_id": "python-new",
    "name": "Python (New)",
    "match_score": 1.0,
    "job_levels": ["Mid-Professional"],
    "test_types": ["K"],
    "duration_minutes": 60
  }
]
```

---

## Frontend (Streamlit)

Features:

* Job description input
* Slider to control number of recommendations
* Clean UI with ranking and metadata
* Real-time API integration

---

## Deployment Strategy

Due to heavy ML dependencies (`torch`, `faiss`, `sentence-transformers`), free-tier platforms have strict limits.

### Recommended Setup:

| Component                 | Platform            |
| ------------------------- | ------------------- |
| Backend (FastAPI + FAISS) | Hugging Face Spaces |
| Frontend (Streamlit)      | Streamlit Cloud     |

This avoids:

* Docker image size limits
* Build failures
* Cold-start issues

---

## Key Highlights

* End-to-end **GenAI recommendation system**
* **RAG-style semantic retrieval**
* Real-world **data engineering pipeline**
* Evaluation with **IR metrics**
* Production-grade API & UI
* Interview-ready architecture

---


