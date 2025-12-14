# src/evaluate_clusters.py

import pandas as pd
import json
import mlflow
import os
from pathlib import Path

# Force MLflow to use a local directory inside the repo (safe for CI/CD and tests)
mlflow.set_tracking_uri("file://" + os.path.join(os.getcwd(), "experiments/mlruns"))
mlflow.set_experiment("cluster_evaluation")

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_assignments(graph_csv: Path, semantic_csv: Path):
    """Load cluster assignment CSVs into DataFrames."""
    graph_df = pd.read_csv(graph_csv)
    semantic_df = pd.read_csv(semantic_csv)
    return graph_df, semantic_df


def evaluate():
    """Compare graph and semantic cluster assignments, log artifacts and results."""
    graph_csv = REPO_ROOT / "output" / "cluster_assignments.csv"
    semantic_csv = REPO_ROOT / "output" / "semantic_clusters.csv"

    if not graph_csv.exists() or not semantic_csv.exists():
        raise FileNotFoundError("Cluster assignment CSVs not found")

    graph_df, semantic_df = load_assignments(graph_csv, semantic_csv)

    # --- Simple evaluation logic ---
    # Align on terms
    merged = pd.merge(graph_df, semantic_df, on="term", suffixes=("_graph", "_semantic"))
    total_terms = len(merged)
    agreement = (merged["cluster_id_graph"] == merged["cluster_id_semantic"]).sum()
    agreement_ratio = agreement / total_terms if total_terms > 0 else 0.0

    results = {
        "total_terms": total_terms,
        "agreement_count": int(agreement),
        "agreement_ratio": agreement_ratio,
    }

    # Save results JSON
    results_file = REPO_ROOT / "output" / "clustering_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Clustering results written to {results_file}")

    # --- MLflow logging ---
    with mlflow.start_run(run_name="cluster_evaluation"):
        mlflow.log_artifact(str(graph_csv), artifact_path="clusters")
        mlflow.log_artifact(str(semantic_csv), artifact_path="clusters")
        mlflow.log_artifact(str(results_file), artifact_path="evaluation")
        mlflow.log_metrics({"agreement_ratio": agreement_ratio})


if __name__ == "__main__":
    evaluate()
