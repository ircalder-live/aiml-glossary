# src/cluster_terms.py
import subprocess

def run_script(script):
    print(f"Running {script}...")
    subprocess.run(["python3", f"src/{script}"], check=True)

def main():
    # Run graph clustering
    run_script("cluster_analysis.py")
    # Run semantic clustering
    run_script("semantic_clustering.py")
    # Run combined clustering + ARI comparison
    run_script("clustering.py")
    # Run evaluation/dashboard
    run_script("evaluate_clusters.py")

if __name__ == "__main__":
    main()
