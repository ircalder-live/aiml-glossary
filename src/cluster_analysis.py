# src/cluster_analysis.py
"""
Graph-based clustering analysis of glossary terms.
Builds a graph from the link dictionary and applies clustering.
Saves assignments and statistics to output artifacts.
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from src.utils import resolve_uri, load_glossary


def run_clustering(glossary_json: str, link_dict_json: str) -> None:
    """Run graph-based clustering using URIs for input/output."""
    glossary_dict = load_glossary(glossary_json)
    link_dict_path = resolve_uri(link_dict_json)

    if not link_dict_path.exists():
        raise FileNotFoundError(f"Link dictionary file not found: {link_dict_path}")

    # Load link dictionary
    with open(link_dict_path, "r", encoding="utf-8") as f:
        link_dict = json.load(f)

    # Build graph
    G = nx.Graph()
    for term in glossary_dict.keys():
        G.add_node(term)
    for term, links in link_dict.items():
        for link in links:
            if link in glossary_dict:
                G.add_edge(term, link)

    # Apply clustering (connected components as simple clusters)
    clusters = list(nx.connected_components(G))
    assignments = {}
    for idx, cluster in enumerate(clusters):
        for term in cluster:
            assignments[term] = idx

    # Save cluster assignments
    assignments_file = resolve_uri("output:cluster_assignments.csv")
    with open(assignments_file, "w", encoding="utf-8") as f:
        f.write("term,cluster\n")
        for term, cluster_id in assignments.items():
            f.write(f"{term},{cluster_id}\n")

    # Save graph stats
    stats = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "num_clusters": len(clusters),
        "cluster_sizes": [len(c) for c in clusters],
    }
    stats_file = resolve_uri("output:graph_stats.json")
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # Visualization
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx(
        G,
        pos,
        with_labels=True,
        node_color=[assignments[n] for n in G.nodes()],
        cmap=plt.cm.tab20,
        node_size=500,
        font_size=8,
    )
    viz_file = resolve_uri("visualizations:glossary_clusters.png")
    plt.savefig(viz_file, dpi=300)
    plt.close()

    print(f"Cluster assignments written to {assignments_file}")
    print(f"Graph stats written to {stats_file}")
    print(f"Visualization written to {viz_file}")


def main() -> None:
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 -m src.cluster_analysis <glossary_json> <link_dict_json>")
        sys.exit(1)
    run_clustering(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
