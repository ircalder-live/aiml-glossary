# src/semantic_clustering.py

import json
import csv
from pathlib import Path
import mlflow
import os

# Force MLflow to use a local directory inside the repo (safe for CI/CD and tests)
mlflow.set_tracking_uri("file://" + os.path.join(os.getcwd(), "experiments/mlruns"))
mlflow.set_experiment("semantic_clustering")

# Resolve repo root
REPO_ROOT = Path(__file__).resolve().parent.parent


def run_semantic_clustering(
    glossary_file: Path = REPO_ROOT / "data" / "aiml_glossary.json",
    output_dir: Path = Path("output"),
    vis_dir: Path = Path("visualizations")
):
    """
    Perform semantic clustering on glossary terms.
    Saves JSON, CSV assignments, visualization, and logs artifacts with MLflow.
    """
    glossary_file = Path(glossary_file)
    output_dir = Path(output_dir)
    vis_dir = Path(vis_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)

    if not glossary_file.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_file}")

    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    # --- Dummy semantic clustering logic ---
    # Replace with actual embeddings + clustering if available
    terms = [entry["term"] for entry in glossary if "term" in entry]
    semantic_partition = {term: i for i, term in enumerate(terms)}

    # Save JSON
    semantic_json = output_dir / "semantic_clusters.json"
    with open(semantic_json, "w", encoding="utf-8") as f:
        json.dump(semantic_partition, f, indent=2)
    print(f"Semantic clustering results written to {semantic_json}")

    # Save CSV (required by evaluate_clusters.py)
    semantic_csv = output_dir / "semantic_clusters.csv"
    with open(semantic_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "cluster_id"])
        for term, cluster_id in semantic_partition.items():
            writer.writerow([term, cluster_id])
    print(f"Semantic cluster assignments written to {semantic_csv}")

    # Visualization placeholder
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 6))
    plt.scatter(range(len(terms)), [0] * len(terms), c=range(len(terms)), cmap="tab20", s=50)
    plt.xticks(range(len(terms)), terms, rotation=90)
    plt.yticks([])
    vis_file = vis_dir / "semantic_clusters.png"
    plt.tight_layout()
    plt.savefig(vis_file, dpi=150)
    plt.close()
    print(f"Semantic clustering visualization saved to {vis_file}")

    # --- MLflow logging ---
    with mlflow.start_run(run_name="semantic_clustering"):
        mlflow.log_artifact(str(semantic_json), artifact_path="clusters")
        mlflow.log_artifact(str(semantic_csv), artifact_path="clusters")
        mlflow.log_artifact(str(vis_file), artifact_path="visualizations")

    return semantic_partition


if __name__ == "__main__":
    run_semantic_clustering()
