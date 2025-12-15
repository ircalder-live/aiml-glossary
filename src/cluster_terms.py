# src/cluster_terms.py
"""
Cluster orchestration script.
Runs graph clustering, semantic clustering, and evaluation in sequence.
Designed for consistent local and CI/CD execution.
"""

import subprocess
from pathlib import Path
from src.cluster_analysis import run_clustering
from src.semantic_clustering import run_semantic_clustering

# --- Repo root and directories ---
REPO_ROOT = Path(__file__).resolve().parent.parent
(REPO_ROOT / "output").mkdir(parents=True, exist_ok=True)
(REPO_ROOT / "visualizations").mkdir(parents=True, exist_ok=True)
(REPO_ROOT / "experiments" / "mlruns").mkdir(parents=True, exist_ok=True)


def run_module(module: str) -> None:
    """Helper to run another src module via subprocess."""
    subprocess.run(["python3", "-m", module], check=True)


def main() -> None:
    """Run clustering pipeline: graph, semantic, then evaluation."""
    print("▶ Running cluster_analysis...")
    run_clustering(
        str(REPO_ROOT / "data" / "aiml_glossary.json"),
        str(REPO_ROOT / "data" / "link_dictionary.json"),
    )

    print("▶ Running semantic_clustering...")
    run_semantic_clustering(str(REPO_ROOT / "data" / "aiml_glossary.json"))

    print("▶ Running evaluate_clusters...")
    run_module("src.evaluate_clusters")

    # Publishing handled by Makefile `publish` target


if __name__ == "__main__":
    main()
