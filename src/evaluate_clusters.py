# src/evaluate_clusters.py
"""
Evaluate clustering results by comparing graph-based and semantic assignments.
Computes metrics like Adjusted Rand Index (ARI) and saves results to output.
"""

import json
from sklearn.metrics import adjusted_rand_score
from src.utils import resolve_uri, load_glossary


def evaluate_clusters(glossary_json: str = "data:aiml_glossary.json") -> dict:
    """
    Evaluate clustering results using URIs for input/output.
    Optionally loads glossary via load_glossary() to ensure consistent normalization.
    """
    # Ensure glossary loads cleanly (normalization handled by load_glossary)
    glossary_dict = load_glossary(glossary_json)
    if not glossary_dict:
        raise ValueError("Glossary is empty or invalid.")

    graph_assignments_file = resolve_uri("output:cluster_assignments.csv")
    semantic_assignments_file = resolve_uri("output:semantic_cluster_assignments.csv")

    if not graph_assignments_file.exists():
        raise FileNotFoundError(
            f"Graph assignments file not found: {graph_assignments_file}"
        )
    if not semantic_assignments_file.exists():
        raise FileNotFoundError(
            f"Semantic assignments file not found: {semantic_assignments_file}"
        )

    # Load assignments
    graph_assignments = {}
    with open(graph_assignments_file, "r", encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            term, cluster = line.strip().split(",")
            graph_assignments[term] = int(cluster)

    semantic_assignments = {}
    with open(semantic_assignments_file, "r", encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            term, cluster = line.strip().split(",")
            semantic_assignments[term] = int(cluster)

    # Align terms (only those present in both assignments and glossary)
    common_terms = (
        set(graph_assignments.keys())
        & set(semantic_assignments.keys())
        & set(glossary_dict.keys())
    )
    graph_labels = [graph_assignments[t] for t in common_terms]
    semantic_labels = [semantic_assignments[t] for t in common_terms]

    # Compute ARI
    ari = adjusted_rand_score(graph_labels, semantic_labels)

    metrics = {
        "num_terms_compared": len(common_terms),
        "ari": ari,
    }

    # Save metrics
    metrics_file = resolve_uri("output:ari_metrics.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"ARI metrics written to {metrics_file}")
    return metrics


def main() -> None:
    metrics = evaluate_clusters()
    print("Cluster Evaluation Summary:")
    print(metrics)


if __name__ == "__main__":
    main()
