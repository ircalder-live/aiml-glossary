# src/clustering.py

from pathlib import Path
import json
from sklearn.metrics import adjusted_rand_score
import mlflow
import os

# Force MLflow to use a local directory inside the repo (safe for CI/CD)
mlflow.set_tracking_uri("file://" + os.path.join(os.getcwd(), "experiments/mlruns"))

# Resolve repo root (two levels up from this file)
REPO_ROOT = Path(__file__).resolve().parent.parent


def run_clustering(
    glossary_file: Path = REPO_ROOT / "data" / "aiml_glossary.json",
    output_dir: Path = REPO_ROOT / "output"
):
    """
    Perform a clustering comparison and log results with MLflow.
    """
    glossary_file = Path(glossary_file)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load glossary terms
    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    terms = [entry["term"] for entry in glossary if "term" in entry]

    # Dummy clustering comparison (replace with your actual logic)
    labels_a = [0] * len(terms)
    labels_b = [1] * len(terms)
    score = adjusted_rand_score(labels_a, labels_b)

    results = {
        "num_terms": len(terms),
        "adjusted_rand_score": score
    }
    results_file = output_dir / "clustering_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Clustering results written to {results_file}")

    # --- MLflow logging ---
    with mlflow.start_run(run_name="clustering"):
        mlflow.log_artifact(str(results_file), artifact_path="results")
        mlflow.log_dict(results, "clustering_summary.json")

    return results


if __name__ == "__main__":
    run_clustering()
