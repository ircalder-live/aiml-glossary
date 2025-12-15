# src/clustering.py
"""
Unified clustering pipeline.
Runs both graph-based and semantic clustering, then evaluates results.
Designed for reproducible local and CI/CD execution with URI-based paths.
"""

import sys
from src.cluster_analysis import run_clustering
from src.semantic_clustering import run_semantic_clustering
from src.evaluate_clusters import evaluate_clusters
from src.utils import resolve_uri, load_glossary


def run_pipeline(
    glossary_file: str, link_dict_file: str, num_clusters: int = 8
) -> None:
    """Run full clustering pipeline: graph clustering, semantic clustering, evaluation."""
    # Ensure glossary loads cleanly (normalization handled by load_glossary)
    glossary_dict = load_glossary(glossary_file)
    if not glossary_dict:
        raise ValueError("Glossary is empty or invalid.")

    link_dict_path = resolve_uri(link_dict_file)
    if not link_dict_path.exists():
        raise FileNotFoundError(f"Link dictionary file not found: {link_dict_path}")

    print("▶ Running graph-based clustering...")
    run_clustering(glossary_file, link_dict_file)

    print("▶ Running semantic clustering...")
    run_semantic_clustering(glossary_file, num_clusters=num_clusters)

    print("▶ Evaluating clusters...")
    metrics = evaluate_clusters()
    print("\n📊 Dashboard Summary")
    print(metrics)


def main() -> None:
    """Entry point for CLI execution."""
    if len(sys.argv) < 3:
        print(
            "Usage: python3 -m src.clustering <glossary_file> <link_dict_file> [num_clusters]"
        )
        sys.exit(1)

    glossary_file = sys.argv[1]
    link_dict_file = sys.argv[2]
    num_clusters = int(sys.argv[3]) if len(sys.argv) > 3 else 8

    run_pipeline(glossary_file, link_dict_file, num_clusters)


if __name__ == "__main__":
    main()
