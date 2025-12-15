# src/semantic_clustering.py
"""
Semantic clustering of glossary terms using embeddings.
Groups terms into clusters based on semantic similarity.
Saves assignments and visualization to output artifacts.
"""

import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from src.utils import resolve_uri, load_glossary


def run_semantic_clustering(glossary_json: str, num_clusters: int = 8) -> None:
    """Run semantic clustering using URIs for input/output."""
    glossary_dict = load_glossary(glossary_json)

    terms = list(glossary_dict.keys())
    definitions = list(glossary_dict.values())

    # Vectorize definitions
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(definitions)

    # KMeans clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # Save assignments
    assignments_file = resolve_uri("output:semantic_cluster_assignments.csv")
    with open(assignments_file, "w", encoding="utf-8") as f:
        f.write("term,cluster\n")
        for term, cluster_id in zip(terms, labels):
            f.write(f"{term},{cluster_id}\n")

    # Save cluster size distribution visualization
    cluster_sizes = [list(labels).count(i) for i in range(num_clusters)]
    plt.figure(figsize=(8, 6))
    plt.bar(range(num_clusters), cluster_sizes, color="skyblue")
    plt.xlabel("Cluster ID")
    plt.ylabel("Number of Terms")
    plt.title("Semantic Cluster Sizes")
    viz_file = resolve_uri("visualizations:semantic_clusters.png")
    plt.savefig(viz_file, dpi=300)
    plt.close()

    print(f"Semantic cluster assignments written to {assignments_file}")
    print(f"Visualization written to {viz_file}")


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python3 -m src.semantic_clustering <glossary_json> [num_clusters]"
        )
        sys.exit(1)

    glossary_json = sys.argv[1]
    num_clusters = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    run_semantic_clustering(glossary_json, num_clusters)


if __name__ == "__main__":
    main()
