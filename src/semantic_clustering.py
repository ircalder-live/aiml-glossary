# src/semantic_clustering.py

from pathlib import Path
import json
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import mlflow
import os

# Force MLflow to use a local directory inside the repo (safe for CI/CD)
mlflow.set_tracking_uri("file://" + os.path.join(os.getcwd(), "experiments/mlruns"))

# Resolve repo root (two levels up from this file)
REPO_ROOT = Path(__file__).resolve().parent.parent


def run_semantic_clustering(
    glossary_file: Path = REPO_ROOT / "data" / "aiml_glossary.json",
    output_dir: Path = REPO_ROOT / "output",
    vis_dir: Path = REPO_ROOT / "visualizations"
):
    """
    Perform semantic clustering on glossary terms using TF-IDF + KMeans,
    save outputs, visualize, and log with MLflow.
    """
    glossary_file = Path(glossary_file)
    output_dir = Path(output_dir)
    vis_dir = Path(vis_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)

    # Load glossary terms
    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    terms = [entry["term"] for entry in glossary if "term" in entry]

    # Vectorize terms
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(terms)

    # Cluster terms
    kmeans = KMeans(n_clusters=min(5, len(terms)), random_state=42)
    labels = kmeans.fit_predict(X)

    clusters = {term: int(label) for term, label in zip(terms, labels)}

    # Save clustering results
    results = {
        "num_terms": len(terms),
        "num_clusters": len(set(labels)),
        "clusters": clusters
    }
    results_file = output_dir / "semantic_clusters.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Semantic clustering results written to {results_file}")

    # Visualization
    plt.figure(figsize=(8, 6))
    plt.scatter(X[:, 0].toarray(), X[:, 1].toarray(), c=labels, cmap="tab10", s=50)
    vis_file = vis_dir / "semantic_clusters.png"
    plt.savefig(vis_file, dpi=150)
    plt.close()
    print(f"Semantic clustering visualization saved to {vis_file}")

    # --- MLflow logging ---
    with mlflow.start_run(run_name="semantic_clustering"):
        mlflow.log_artifact(str(results_file), artifact_path="clusters")
        mlflow.log_artifact(str(vis_file), artifact_path="visualizations")
        mlflow.log_dict(results, "semantic_summary.json")

    return results, clusters


if __name__ == "__main__":
    run_semantic_clustering()
