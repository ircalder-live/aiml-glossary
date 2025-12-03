import json
import mlflow
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import community  # python-louvain
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

# --- Load glossary ---
with open("data/aiml_glossary.json", "r", encoding="utf-8") as f:
    glossary = json.load(f)

terms = [entry.get("term", "") for entry in glossary]
definitions = [entry.get("definition", "") for entry in glossary]

# --- Build graph ---
G = nx.Graph()
for entry in glossary:
    term = entry.get("term")
    if not term:
        continue
    G.add_node(term)
    for rel in entry.get("related_terms", []):
        rel_term = rel["label"] if isinstance(rel, dict) else rel
        if rel_term:
            G.add_edge(term, rel_term)
    for tag in entry.get("tags", []):
        tag_term = tag["label"] if isinstance(tag, dict) else tag
        if tag_term:
            G.add_edge(term, tag_term)

num_terms = len(G.nodes)
num_links = len(G.edges)
avg_degree = sum(dict(G.degree()).values()) / num_terms

# --- Graph clustering (Louvain) ---
partition = community.best_partition(G)
graph_clusters = [partition.get(term, -1) for term in terms]
cluster_df = pd.DataFrame(list(partition.items()), columns=["term", "graph_cluster"])
cluster_df.to_csv("cluster_assignments.csv", index=False)

# --- Semantic clustering (TF-IDF + KMeans) ---
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(definitions)
k = 5
kmeans = KMeans(n_clusters=k, random_state=42)
semantic_clusters = kmeans.fit_predict(X)
semantic_df = pd.DataFrame({"term": terms, "semantic_cluster": semantic_clusters})
semantic_df.to_csv("semantic_clusters.csv", index=False)

# --- Compare clusters (ARI) ---
ari = adjusted_rand_score(graph_clusters, semantic_clusters)

# --- Dashboard plots ---
# ARI trend (single run, but saved for MLflow)
plt.figure(figsize=(6, 4))
plt.bar(["ARI"], [ari], color="skyblue")
plt.title("Adjusted Rand Index (Graph vs Semantic)")
plt.ylabel("ARI")
plt.tight_layout()
plt.savefig("ari_bar.png")

# --- Log to MLflow ---
mlflow.set_experiment("AIML Glossary Analysis")
with mlflow.start_run(run_name="Cluster Analysis Pipeline"):
    # Parameters
    mlflow.log_param("num_terms", num_terms)
    mlflow.log_param("num_links", num_links)
    mlflow.log_param("num_clusters_graph", len(set(graph_clusters)))
    mlflow.log_param("num_clusters_semantic", k)

    # Metrics
    mlflow.log_metric("avg_degree", avg_degree)
    mlflow.log_metric("adjusted_rand_index", ari)

    # Artifacts
    mlflow.log_artifact("data/aiml_glossary.json")
    mlflow.log_artifact("cluster_assignments.csv")
    mlflow.log_artifact("semantic_clusters.csv")
    mlflow.log_artifact("ari_bar.png")
