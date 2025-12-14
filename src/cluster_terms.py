# src/cluster_terms.py

import subprocess
from pathlib import Path

# Import sibling modules directly (no "src." prefix)
from cluster_analysis import run_clustering
from semantic_clustering import run_semantic_clustering


def run_script(script: str):
    """Helper to run another script in src/ via subprocess."""
    subprocess.run(["python3", f"src/{script}"], check=True)


def main():
    # Run graph clustering
    print("Running cluster_analysis.py...")
    run_clustering("data/aiml_glossary.json", "data/link_dictionary.json")

    # Run semantic clustering
    print("Running semantic_clustering.py...")
    run_semantic_clustering("data/aiml_glossary.json")

    # Evaluate clusters
    print("Running evaluate_clusters.py...")
    run_script("evaluate_clusters.py")


if __name__ == "__main__":
    main()
