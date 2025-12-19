# src/cluster_analysis.py

"""
Graph-based clustering analysis.
Builds a term graph from glossary + link dictionary, assigns clusters,
exports assignments to CSV, logs artifacts into MLflow, and saves a visualization.
"""

import json
import csv
from pathlib import Path
import sys
import networkx as nx
from networkx.algorithms import community
import mlflow
import matplotlib.pyplot as plt


def run_clustering(
    glossary_json: str,
    link_dict_json: str,
    output_file: str = "data/cluster_assignments.csv"
):
    """
    Perform graph-based clustering using glossary and link dictionary.
    - Resolves paths relative to repo root.
    - Builds a NetworkX graph of terms and links.
    - Detects communities with greedy modularity.
    - Exports cluster assignments to CSV (default: data/cluster_assignments.csv).
    - Logs graph and assignments into MLflow.
    - Saves visualization into visualizations/glossary_clusters.png.
    """

    repo_root = Path(__file__).resolve().parent.parent
    glossary_path = (repo_root / glossary_json).resolve()
    link_dict_path = (repo_root / link_dict_json).resolve()
    output_path = (repo_root / output_file).resolve()

    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")
    if not link_dict_path.exists():
        raise FileNotFoundError(f"Link dictionary file not found: {link_dict_path}")

    # Load glossary
    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_dict = json.load(f)

    # Load link dictionary
    with open(link_dict_path, "r", encoding="utf-8") as f:
        link_dict = json.load(f)

    # Build graph
    G = nx.Graph()
    for term in link_dict.keys():
        G.add_node(term)
    for term, links in link_dict.items():
        for other in links:
            if other in link_dict:
                G.add_edge(term, other)

    # Detect communities
    communities = community.greedy_modularity_communities(G)

    # Build assignments
    assignments = {}
    for idx, comm in enumerate(communities):
        for term in comm:
            assignments[term] = idx

    # Save assignments to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "cluster"])
        for term, cluster in assignments.items():
            writer.writerow([term, cluster])

    print(f"✅ Graph cluster assignments saved: {output_path}")

    # --- Visualization ---
    viz_path = repo_root / "visualizations/glossary_clusters.png"
    viz_path.parent.mkdir(parents=True, exist_ok=True)

    node_colors = [assignments.get(node, -1) for node in G.nodes()]
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, cmap=plt.cm.tab20, node_size=100)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(viz_path, dpi=300)
    plt.close()
    print(f"📈 Cluster visualization saved: {viz_path}")

    # Log to MLflow
    try:
        with mlflow.start_run(run_name="graph_clustering", nested=True):
            nx.write_gml(G, str(repo_root / "data/clustering_graph.gml"))
            mlflow.log_artifact(str(output_path), artifact_path="graph_clusters")
            mlflow.log_artifact(str(repo_root / "data/clustering_graph.gml"), artifact_path="graph_clusters")
            mlflow.log_artifact(str(viz_path), artifact_path="graph_clusters")
            mlflow.log_param("nodes", G.number_of_nodes())
            mlflow.log_param("edges", G.number_of_edges())
            mlflow.log_param("communities", len(communities))
            print("📊 Graph clustering logged to MLflow")
    except Exception as e:
        print(f"⚠️ MLflow logging skipped: {e}")

    return G


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m src.cluster_analysis <glossary_json> <link_dict_json> [output_file]")
        sys.exit(1)

    glossary_json = sys.argv[1]
    link_dict_json = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "data/cluster_assignments.csv"

    run_clustering(glossary_json, link_dict_json, output_file)
