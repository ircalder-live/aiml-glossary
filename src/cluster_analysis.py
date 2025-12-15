# src/cluster_analysis.py

import json
import networkx as nx
from pathlib import Path
from src.utils import load_glossary, resolve_uri


def build_graph(glossary_file: str, link_dict_file: str) -> nx.Graph:
    """
    Build a graph from glossary and link_dict JSON files.

    Parameters
    ----------
    glossary_file : str
        URI or path to glossary JSON file.
    link_dict_file : str
        URI or path to link dictionary JSON file.

    Returns
    -------
    nx.Graph
        Graph with terms as nodes and related terms as edges.
    """
    # load_glossary returns a dict {term: definition}
    glossary = load_glossary(glossary_file)

    # Resolve and load link_dict JSON
    link_dict_path = resolve_uri(link_dict_file)
    link_dict = json.loads(link_dict_path.read_text())

    G = nx.Graph()

    # Add nodes from glossary terms
    for term in glossary.keys():
        G.add_node(term)

    # Add edges from link_dict
    for src, targets in link_dict.items():
        for tgt in targets:
            G.add_edge(src, tgt)

    return G


def run_clustering(
    glossary_file: str,
    link_dict_file: str,
    assignments_path: str = "output/cluster_assignments.csv",
    stats_path: str = "output/graph_stats.json",
    viz_path: str = "visualizations/glossary_clusters.png",
) -> nx.Graph:
    """
    Build the glossary graph, run a simple clustering, and save artifacts.
    """
    import os
    import matplotlib.pyplot as plt

    # Ensure directories exist
    os.makedirs(Path(assignments_path).parent, exist_ok=True)
    os.makedirs(Path(stats_path).parent, exist_ok=True)
    os.makedirs(Path(viz_path).parent, exist_ok=True)

    G = build_graph(glossary_file, link_dict_file)

    # Simple clustering: connected components
    clusters = list(nx.connected_components(G))
    assignments = []
    for i, cluster in enumerate(clusters):
        for term in cluster:
            assignments.append(f"{term},{i}")

    Path(assignments_path).write_text("\n".join(assignments))

    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "num_clusters": len(clusters),
    }
    Path(stats_path).write_text(json.dumps(stats, indent=2))

    # Visualization
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray")
    plt.savefig(viz_path, bbox_inches="tight")
    plt.close()

    return G


def visualize_clusters(
    G: nx.Graph, output_path: str = "visualizations/glossary_clusters.png"
):
    """
    Save a visualization of the glossary graph to a PNG file.
    """
    import os
    import matplotlib.pyplot as plt

    os.makedirs(Path(output_path).parent, exist_ok=True)

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
