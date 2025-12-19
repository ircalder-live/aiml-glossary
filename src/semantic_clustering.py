# src/semantic_clustering.py

"""
Semantic clustering analysis.
Uses embeddings to cluster glossary terms, exports assignments to CSV,
logs artifacts into MLflow, and saves a visualization.
"""

import json
import csv
from pathlib import Path
import sys
import mlflow
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def run_semantic_clustering(
    glossary_json: str,
    output_file: str = "data/semantic_cluster_assignments.csv",
    n_clusters: int = 10,
):
    """
    Perform semantic clustering using embeddings.
    - Loads glossary JSON.
    - Generates embeddings (placeholder: random vectors for demo).
    - Clusters with KMeans.
    - Exports assignments to CSV (default: data/semantic_cluster_assignments.csv).
    - Logs artifacts into MLflow.
    - Saves visualization into visualizations/semantic_clusters.png.
    """

    repo_root = Path(__file__).resolve().parent.parent
    glossary_path = (repo_root / glossary_json).resolve()
    output_path = (repo_root / output_file).resolve()

    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")

    # Load glossary
    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_dict = json.load(f)

    terms = list(glossary_dict.keys())

    # Placeholder embeddings (replace with real model)
    rng = np.random.default_rng(seed=42)
    embeddings = rng.normal(size=(len(terms), 50))

    # Cluster with KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(embeddings)

    # Save assignments to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "cluster"])
        for term, cluster in zip(terms, clusters):
            writer.writerow([term, cluster])

    print(f"✅ Semantic cluster assignments saved: {output_path}")

    # --- Visualization ---
    viz_path = repo_root / "visualizations/semantic_clusters.png"
    viz_path.parent.mkdir(parents=True, exist_ok=True)

    # Reduce to 2D with PCA
    pca = PCA(n_components=2, random_state=42)
    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(10, 8))
    plt.scatter(reduced[:, 0], reduced[:, 1], c=clusters, cmap=plt.cm.tab20, s=30)
    plt.title("Semantic Clusters (PCA projection)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    plt.savefig(viz_path, dpi=300)
    plt.close()
    print(f"📈 Semantic cluster visualization saved: {viz_path}")

    # Log to MLflow
    try:
        with mlflow.start_run(run_name="semantic_clustering", nested=True):
            mlflow.log_artifact(str(output_path), artifact_path="semantic_clusters")
            mlflow.log_artifact(str(viz_path), artifact_path="semantic_clusters")
            mlflow.log_param("terms", len(terms))
            mlflow.log_param("clusters", n_clusters)
            print("📊 Semantic clustering logged to MLflow")
    except Exception as e:
        print(f"⚠️ MLflow logging skipped: {e}")

    return clusters


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m src.semantic_clustering <glossary_json> [output_file] [n_clusters]"
        )
        sys.exit(1)

    glossary_json = sys.argv[1]
    output_file = (
        sys.argv[2] if len(sys.argv) > 2 else "data/semantic_cluster_assignments.csv"
    )
    n_clusters = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    run_semantic_clustering(glossary_json, output_file, n_clusters)
