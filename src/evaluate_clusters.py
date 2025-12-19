# src/evaluate_clusters.py

import json
import csv
from pathlib import Path
import sys
import mlflow
from sklearn.metrics import adjusted_rand_score


def resolve_uri(uri: str) -> Path:
    """
    Resolve a URI like 'data:filename.csv' into a repo-root Path.
    """
    repo_root = Path(__file__).resolve().parent.parent
    if ":" not in uri:
        return (repo_root / uri).resolve()
    prefix, relpath = uri.split(":", 1)
    if prefix == "data":
        return (repo_root / "data" / relpath).resolve()
    elif prefix == "output":
        return (repo_root / "output" / relpath).resolve()
    else:
        raise ValueError(f"Unknown URI prefix: {prefix}")


def evaluate_clusters(
    graph_assignments_uri: str = "data:cluster_assignments.csv",
    semantic_assignments_uri: str = "data:semantic_cluster_assignments.csv",
):
    """
    Evaluate agreement between graph-based and semantic clustering assignments.
    Produces:
    - data/graph_stats.json with basic counts and agreement ratio
    - data/ari_metrics.json with adjusted Rand index (ARI)
    """

    repo_root = Path(__file__).resolve().parent.parent
    graph_assignments_file = resolve_uri(graph_assignments_uri)
    semantic_assignments_file = resolve_uri(semantic_assignments_uri)

    if not graph_assignments_file.exists():
        raise FileNotFoundError(
            f"Graph assignments file not found: {graph_assignments_file}"
        )
    if not semantic_assignments_file.exists():
        raise FileNotFoundError(
            f"Semantic assignments file not found: {semantic_assignments_file}"
        )

    # Load graph assignments
    graph_assignments = {}
    with open(graph_assignments_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            graph_assignments[row["term"]] = row["cluster"]

    # Load semantic assignments
    semantic_assignments = {}
    with open(semantic_assignments_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            semantic_assignments[row["term"]] = row["cluster"]

    # Compute overlap stats
    common_terms = set(graph_assignments.keys()) & set(semantic_assignments.keys())
    agreements = sum(
        1 for t in common_terms if graph_assignments[t] == semantic_assignments[t]
    )
    total = len(common_terms)
    agreement_ratio = agreements / total if total > 0 else 0.0

    graph_stats = {
        "total_terms": total,
        "agreements": agreements,
        "agreement_ratio": agreement_ratio,
    }

    # Compute ARI
    labels_graph = [graph_assignments[t] for t in common_terms]
    labels_semantic = [semantic_assignments[t] for t in common_terms]
    ari_score = adjusted_rand_score(labels_graph, labels_semantic) if total > 0 else 0.0
    ari_metrics = {"adjusted_rand_index": ari_score}

    # Save both artifacts
    graph_stats_path = repo_root / "data/graph_stats.json"
    ari_metrics_path = repo_root / "data/ari_metrics.json"
    for path, obj in [(graph_stats_path, graph_stats), (ari_metrics_path, ari_metrics)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
        print(f"✅ Saved {path}")

    # Log to MLflow
    try:
        with mlflow.start_run(run_name="evaluate_clusters", nested=True):
            mlflow.log_artifact(
                str(graph_stats_path), artifact_path="cluster_evaluation"
            )
            mlflow.log_artifact(
                str(ari_metrics_path), artifact_path="cluster_evaluation"
            )
            mlflow.log_metric("agreement_ratio", agreement_ratio)
            mlflow.log_metric("adjusted_rand_index", ari_score)
            mlflow.log_param("total_terms", total)
            print("📊 Cluster evaluation logged to MLflow")
    except Exception as e:
        print(f"⚠️ MLflow logging skipped: {e}")

    return {"graph_stats": graph_stats, "ari_metrics": ari_metrics}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        graph_assignments_uri = sys.argv[1]
    else:
        graph_assignments_uri = "data:cluster_assignments.csv"

    if len(sys.argv) > 2:
        semantic_assignments_uri = sys.argv[2]
    else:
        semantic_assignments_uri = "data:semantic_cluster_assignments.csv"

    evaluate_clusters(graph_assignments_uri, semantic_assignments_uri)
