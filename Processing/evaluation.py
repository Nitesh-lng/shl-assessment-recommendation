import json
from pathlib import Path
from typing import List, Dict

from retrievel import (
    load_vector_store,
    get_mmr_retriever,
    aggregate_chunks_to_assessments,
)

GROUND_TRUTH_PATH = Path("Data/evaluation/ground_truth.json")


def load_ground_truth() -> List[Dict]:
    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_recall_at_k(k: int) -> float:
    vs = load_vector_store()
    retriever = get_mmr_retriever(vs)

    data = load_ground_truth()
    hits = 0

    for item in data:
        query = item["query"]
        gt_ids = set(item["ground_truth_assessment_ids"])

        docs = retriever.invoke(query)
        recs = aggregate_chunks_to_assessments(docs, top_n=k)

        retrieved_ids = {r["assessment_id"] for r in recs}

        if retrieved_ids.intersection(gt_ids):
            hits += 1

    return hits / len(data)


def evaluate_mrr() -> float:
    vs = load_vector_store()
    retriever = get_mmr_retriever(vs)

    data = load_ground_truth()
    reciprocal_ranks = []

    for item in data:
        query = item["query"]
        gt_ids = set(item["ground_truth_assessment_ids"])

        docs = retriever.invoke(query)
        recs = aggregate_chunks_to_assessments(docs, top_n=10)

        rank = 0
        for idx, rec in enumerate(recs, start=1):
            if rec["assessment_id"] in gt_ids:
                rank = idx
                break

        if rank > 0:
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

    return sum(reciprocal_ranks) / len(reciprocal_ranks)


if __name__ == "__main__":
    r5 = evaluate_recall_at_k(5)
    r10 = evaluate_recall_at_k(10)
    mrr = evaluate_mrr()

    print("\nEvaluation Results")
    print(f"Recall@5  = {r5:.2f}")
    print(f"Recall@10 = {r10:.2f}")
    print(f"MRR       = {mrr:.2f}")
