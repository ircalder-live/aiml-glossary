import os
import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import mlflow
import community  # python-louvain

def build_graph(glossary_file="data/aiml_glossary.json",
                link_dict_file="data/link_dictionary.json"):
    """Construct a NetworkX graph from glossary entries and link dictionary."""
    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)
    with open(link_dict_file, "r", encoding="utf-8") as f:
        link_dict = json.load(f)

    G = nx.Graph()

    # Add nodes for each term
    for entry in glossary:
        term = entry.get("term")
        if term:
            G.add_node(term)

    # Add edges for related terms
    for entry in glossary:
        term = entry.get("term")
        if not term:
            continue
        for rel in entry.get("related_terms", []):
            if isinstance(rel, dict):
                rel_term = rel.get("label")
            else:
                rel_term = str(rel).strip()
            if rel_term and rel_term in G.nodes:
                G.add_edge(term, rel_term)

    return G

def run_clustering(glossary_file="data/aiml_glossary.json",
                   link_dict_file="data/link_dictionary.json"):
    G = build_graph(glossary_file, link_dict_file)

    num_terms = G.number_of_nodes()
    num_links = G.number_of_edges()
    avg_degree = sum(dict(G.degree()).values()) / num_terms if num_terms > 0 else 0

    # Louvain partition
    partition = community.best_partition(G)

    num_clusters = len(set(partition.values()))
    largest_cluster_size = max(pd.Series(list(partition.values())).value_counts())
    modularity = community.modularity(partition, G)

    # Save cluster assignments
    os.makedirs("output", exist_ok=True)
    cluster_df = pd.DataFrame(list(partition.items()), columns=["term", "cluster_id"])
    cluster_df.to_csv("output/cluster_assignments.csv", index=False)

    # Visualization
    os.makedirs("visualizations", exist_ok=True)
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos,
                           node_color=[partition[n] for n in G.nodes],
                           cmap=plt.cm.Set3)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title("Glossary Clusters (Louvain)")
    plt.tight_layout()
    plt.savefig("visualizations/glossary_clusters.png")

    # MLflow logging
    with mlflow.start_run(run_name="Glossary Clustering Experiment"):
        mlflow.log_param("num_terms", num_terms)
        mlflow.log_param("num_links", num_links)
        mlflow.log_metric("avg_degree", avg_degree)
        mlflow.log_metric("num_clusters", num_clusters)
        mlflow.log_metric("largest_cluster_size", largest_cluster_size)
        mlflow.log_metric("modularity", modularity)

        mlflow.log_artifact(glossary_file)
        mlflow.log_artifact(link_dict_file)
        mlflow.log_artifact("output/cluster_assignments.csv")
        mlflow.log_artifact("visualizations/glossary_clusters.png")

    print(f"Clustering complete: {num_clusters} clusters, modularity={modularity:.3f}")

if __name__ == "__main__":
    run_clustering()
