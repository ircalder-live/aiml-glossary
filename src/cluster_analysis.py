# src/cluster_analysis.py

import json
import csv
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import mlflow
import os

# Force MLflow to use a local directory inside the repo (safe for CI/CD and tests)
mlflow.set_tracking_uri("file://" + os.path.join(os.getcwd(), "experiments/mlruns"))
# Explicitly set or create a named experiment
mlflow.set_experiment("glossary_clustering")

try:
    import community as community_louvain
except ImportError:
    community_louvain = None


def build_graph(glossary_file: Path, link_dict_file: Path):
    """
    Build a glossary graph from JSON glossary and link dictionary.
    Handles both single-anchor and list-of-anchors cases.
    """
    glossary_file = Path(glossary_file)
    link_dict_file = Path(link_dict_file)

    print("DEBUG: Looking for glossary_file at", glossary_file.resolve())
    print("DEBUG: Looking for link_dict_file at", link_dict_file.resolve())

    if not glossary_file.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_file}")
    if not link_dict_file.exists():
        raise FileNotFoundError(f"Link dictionary file not found: {link_dict_file}")

    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)
    with open(link_dict_file, "r", encoding="utf-8") as f:
        link_dict = json.load(f)

    G = nx.Graph()

    # Add nodes
    for entry in glossary:
        term = entry.get("term")
        if term:
            G.add_node(term)

    # Add edges (support list or single string anchors)
    for term, anchors in link_dict.items():
        if isinstance(anchors, list):
            for anchor in anchors:
                if term in G and anchor in G:
                    G.add_edge(term, anchor)
        else:
            if term in G and anchors in G:
                G.add_edge(term, anchors)

    print(f"DEBUG: Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    return G


def run_clustering(
    glossary_file: Path,
    link_dict_file: Path,
    output_dir: Path = Path("output"),
    vis_dir: Path = Path("visualizations")
):
    """
    Run Louvain clustering on glossary graph, save outputs, visualize, and log with MLflow.
    Outputs are written relative to the current working directory by default.
    """
    glossary_file = Path(glossary_file)
    link_dict_file = Path(link_dict_file)
    output_dir = Path(output_dir)
    vis_dir = Path(vis_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)

    G = build_graph(glossary_file, link_dict_file)

    num_terms = G.number_of_nodes()
    num_links = G.number_of_edges()

    partition = {}
    if community_louvain:
        partition = community_louvain.best_partition(G)
        print(f"DEBUG: Louvain clustering produced {len(set(partition.values()))} clusters")
    else:
        print("WARNING: community_louvain not installed, skipping clustering")

    # Save graph stats (including partition if available)
    graph_df = {
        "num_terms": num_terms,
        "num_links": num_links,
        "num_clusters": len(set(partition.values())) if partition else 0,
        "partition": partition
    }
    stats_file = output_dir / "graph_stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(graph_df, f, indent=2)
    print(f"Graph stats written to {stats_file}")

    # Write cluster assignments CSV if partition exists
    assignments_file = output_dir / "cluster_assignments.csv"
    if partition:
        with open(assignments_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["term", "cluster_id"])
            for term, cluster in partition.items():
                writer.writerow([term, cluster])
        print(f"Cluster assignments written to {assignments_file}")

    # Visualization
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, node_size=50, with_labels=False)
    vis_file = vis_dir / "glossary_clusters.png"
    plt.savefig(vis_file, dpi=150)
    plt.close()
    print(f"Graph visualization saved to {vis_file}")

    # --- MLflow logging ---
    with mlflow.start_run(run_name="glossary_clustering"):
        mlflow.log_artifact(str(stats_file), artifact_path="stats")
        mlflow.log_artifact(str(vis_file), artifact_path="visualizations")
        if assignments_file.exists():
            mlflow.log_artifact(str(assignments_file), artifact_path="clusters")
        mlflow.log_dict(graph_df, "graph_summary.json")

    return graph_df, partition, G


if __name__ == "__main__":
    # Example usage from repo root:
    run_clustering("data/aiml_glossary.json", "data/link_dictionary.json")
