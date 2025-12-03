# src/evaluate_clusters.py
import os
import json
import mlflow
import pandas as pd
from pathlib import Path
from sklearn.metrics import adjusted_rand_score
import matplotlib.pyplot as plt

EXPERIMENT_NAME = "AIML Glossary Analysis"

def load_assignments(graph_csv="output/cluster_assignments.csv",
                     semantic_csv="output/semantic_clusters.csv"):
    graph_df = pd.read_csv(graph_csv)
    semantic_df = pd.read_csv(semantic_csv)
    return graph_df, semantic_df

def compute_ari(graph_df: pd.DataFrame, semantic_df: pd.DataFrame):
    # Align on intersection of terms
    merged = pd.merge(graph_df, semantic_df, on="term", suffixes=("_graph", "_semantic"))
    if merged.empty:
        return 0.0, merged
    ari = adjusted_rand_score(merged["cluster_id_graph"], merged["cluster_id_semantic"])
    return float(ari), merged

def save_metrics(ari: float, out_path="output/ari_metrics.json"):
    Path("output").mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"adjusted_rand_index": ari}, f, indent=2)

def dashboard_plots(mlflow_enable=True):
    # Optional: query MLflow runs to produce ARI trend & bar charts
    if not mlflow_enable:
        return

    try:
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
        if not experiment:
            print("No experiment found; skipping ARI dashboard plots.")
            return

        runs = client.search_runs([experiment.experiment_id])
        ari_data = []
        for run in runs:
            metrics = run.data.metrics
            if "adjusted_rand_index" in metrics:
                ari_data.append({
                    "run_id": run.info.run_id,
                    "run_name": run.data.tags.get("mlflow.runName", ""),
                    "timestamp": run.info.start_time,
                    "adjusted_rand_index": metrics["adjusted_rand_index"],
                })

        if not ari_data:
            print("No ARI metrics found; skipping dashboard plots.")
            return

        df = pd.DataFrame(ari_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.sort_values("timestamp", inplace=True)

        Path("visualizations").mkdir(exist_ok=True)

        # Trend plot
        plt.figure(figsize=(10, 6))
        plt.plot(df["timestamp"], df["adjusted_rand_index"], marker="o", linestyle="-")
        plt.title("Adjusted Rand Index across glossary runs")
        plt.xlabel("Run timestamp")
        plt.ylabel("Adjusted Rand Index")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("visualizations/ari_trend.png")
        plt.close()

        # Bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(df["run_name"], df["adjusted_rand_index"], color="skyblue")
        plt.title("Adjusted Rand Index by run")
        plt.xlabel("Run name")
        plt.ylabel("Adjusted Rand Index")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("visualizations/ari_bar.png")
        plt.close()

        # Log the plots
        run_name = os.getenv("RUN_NAME", f"ari-dashboard-{os.getenv('GITHUB_SHA', 'local')}")
        mlflow.set_experiment(EXPERIMENT_NAME)
        with mlflow.start_run(run_name=run_name):
            mlflow.log_artifact("visualizations/ari_trend.png")
            mlflow.log_artifact("visualizations/ari_bar.png")

    except Exception as e:
        print(f"Dashboard plot generation skipped due to error: {e}")

def evaluate(graph_csv="output/cluster_assignments.csv",
             semantic_csv="output/semantic_clusters.csv",
             metrics_out="output/ari_metrics.json",
             make_dashboard=True):
    graph_df, semantic_df = load_assignments(graph_csv, semantic_csv)
    ari, merged = compute_ari(graph_df, semantic_df)
    save_metrics(ari, metrics_out)

    # MLflow logging for ARI
    mlflow.set_experiment(EXPERIMENT_NAME)
    run_name = os.getenv("RUN_NAME", f"cluster-comparison-{os.getenv('GITHUB_SHA', 'local')}")
    with mlflow.start_run(run_name=run_name):
        mlflow.log_metric("adjusted_rand_index", ari)
        if os.path.exists(graph_csv):
            mlflow.log_artifact(graph_csv)
        if os.path.exists(semantic_csv):
            mlflow.log_artifact(semantic_csv)
        if os.path.exists(metrics_out):
            mlflow.log_artifact(metrics_out)

    print(f"Adjusted Rand Index (graph vs semantic): {ari:.4f}")

    # Optional dashboard plots from historical MLflow runs
    dashboard_plots(mlflow_enable=make_dashboard)

if __name__ == "__main__":
    evaluate()
