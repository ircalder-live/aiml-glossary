# src/semantic_clustering.py
import os
import json
import mlflow
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

EXPERIMENT_NAME = "AIML Glossary Analysis"

def load_glossary(glossary_file="data/aiml_glossary.json"):
    with open(glossary_file, "r", encoding="utf-8") as f:
        return json.load(f)

def run_semantic_clustering(glossary_file="data/aiml_glossary.json", k: int = None, seed: int = 42):
    glossary = load_glossary(glossary_file)
    terms = [entry.get("term", "") for entry in glossary]
    definitions = [entry.get("definition", "") or "" for entry in glossary]

    # Robust TF-IDF: ignore empty-only corpus gracefully
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(definitions)

    # Choose k: env RUN_K overrides, else arg, else heuristic
    env_k = os.getenv("RUN_K")
    k = int(env_k) if env_k else (k if isinstance(k, int) and k > 0 else min(8, max(2, int(np.sqrt(len(terms))))))
    kmeans = KMeans(n_clusters=k, random_state=seed, n_init="auto")
    clusters = kmeans.fit_predict(X)

    # Outputs
    Path("output").mkdir(exist_ok=True)
    Path("visualizations").mkdir(exist_ok=True)

    semantic_df = pd.DataFrame({"term": terms, "cluster_id": clusters})
    semantic_df.to_csv("output/semantic_clusters.csv", index=False)

    # 2D projection for plotting (omit labels for CI readability)
    try:
        X_dense = X.toarray()
        X_2d = PCA(n_components=2, random_state=seed).fit_transform(X_dense)
        plt.figure(figsize=(8, 6))
        plt.scatter(X_2d[:, 0], X_2d[:, 1], c=clusters, cmap="Set3", alpha=0.7, s=20)
        plt.title("Semantic clusters of glossary terms (TF-IDF + KMeans)")
        plt.tight_layout()
        plt.savefig("visualizations/semantic_clusters.png")
        plt.close()
    except Exception as e:
        # In case PCA fails for extreme sparsity; still continue
        print(f"Note: PCA visualization skipped due to: {e}")

    # MLflow logging
    mlflow.set_experiment(EXPERIMENT_NAME)
    run_name = os.getenv("RUN_NAME", f"semantic-clustering-{os.getenv('GITHUB_SHA', 'local')}")
    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("algo", "tfidf-kmeans")
        mlflow.log_param("k", k)
        mlflow.log_param("seed", seed)
        mlflow.log_param("num_terms", len(terms))
        mlflow.log_metric("inertia", float(kmeans.inertia_))
        mlflow.log_artifact(glossary_file)
        mlflow.log_artifact("output/semantic_clusters.csv")
        if os.path.exists("visualizations/semantic_clusters.png"):
            mlflow.log_artifact("visualizations/semantic_clusters.png")

    print(f"Semantic clustering complete: k={k}, inertia={kmeans.inertia_:.3f}")

if __name__ == "__main__":
    # k can be set via env RUN_K or left to heuristic
    run_semantic_clustering()
