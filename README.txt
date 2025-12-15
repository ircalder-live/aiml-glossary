AIML Glossary Project
=====================

![CI](https://github.com/ircalder-live/aiml-glossary/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/ircalder-live/aiml-glossary/actions/workflows/pages.yml/badge.svg)

📖 Overview
-----------
# AIML Glossary Workflow

This project uses a **URI‑based workflow** for reproducibility and contributor clarity.
Instead of fragile filesystem paths, resources are referenced with logical URIs:

- `data:filename.json` → maps to `repo_root/data/filename.json`
- `output:filename.csv` → maps to `repo_root/output/filename.csv`
- `visualizations:filename.png` → maps to `repo_root/visualizations/filename.png`

The resolver in `src/utils.py` ensures these URIs work consistently across local runs and CI/CD.

---

## Runbook

The main workflow is exercised through `notebooks/runbook.ipynb`.
Contributors should run the notebook cell‑by‑cell to generate and verify artifacts.

Expected steps:
1. **Generate outputs** → `output/terms.csv`, `output/glossary_copy.json`
2. **Build link dictionary** → `output/link_dictionary.json`
3. **Enrich glossary** → `output/enriched_glossary.json`
4. **Graph clustering** → `output/cluster_assignments.csv`, `output/graph_stats.json`, `visualizations/glossary_clusters.png`
5. **Semantic clustering** → `output/semantic_cluster_assignments.csv`, `visualizations/semantic_clusters.png`
6. **Evaluate clusters** → `output/ari_metrics.json`
7. **Coverage report** → `output/coverage_report.json` with ✅/❌ markers

---

## Artifact Checklist

At the bottom of the runbook, a Markdown checklist is provided.
Contributors should confirm all expected artifacts are present and marked ✅ before committing.

---

## Quick Start

```bash
# Run the notebook end-to-end
jupyter nbconvert --execute --to notebook notebooks/runbook.ipynb --output notebooks/runbook_executed.ipynb

⚡ Quick Start
--------------
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
2. Generate glossary outputs:
    make outputs
3. Run full clustering analysis (graph + semantic + evaluation):
    make cluster-analysis

Repository structure

aiml-glossary-project/
├── data/                # Raw and processed data
│   ├── aiml_glossary.json
│   └── link_dictionary.json
├── src/                 # Source code for pipeline
│   ├── generate_outputs.py       # Generate Markdown/XHTML glossary and coverage report
│   ├── convert_glossary.py       # Convert Markdown glossary to JSON
│   ├── cluster_analysis.py       # Graph-based clustering (Louvain)
│   ├── semantic_clustering.py    # Definition-based clustering (TF-IDF + KMeans)
│   └── evaluate_clusters.py      # Compare clustering methods (ARI) and dashboard plots
├── output/              # Generated outputs
│   ├── glossary.md
│   ├── glossary.xhtml
│   ├── coverage_report.txt
│   ├── cluster_assignments.csv
│   ├── semantic_clusters.csv
│   └── ari_metrics.json
├── visualizations/      # Saved plots
│   ├── glossary_clusters.png
│   ├── semantic_clusters.png
│   ├── ari_trend.png
│   └── ari_bar.png
├── experiments/         # MLflow artifacts (auto-created)
│   └── mlruns/
├── notebooks/           # Optional Jupyter notebooks
│   └── glossary_analysis.ipynb
|   └── runbook.ipynb
├── requirements.txt     # Python dependencies
├── Makefile             # Workflow automation
└── README.txt           # Project overview

Instructions (bash)
1. Install dependencies
    pip install -r requirements.txt
2. Generate glossary outputs
    make outputs
Produces:
    output/glossary.md
    output/glossary.xhtml
    output/coverage_report.txt
3. Run clustering analysis
    make cluster-analysis
Runs graph clustering, semantic clustering, and evaluation. Produces:
    output/cluster_assignments.csv
    output/semantic_clusters.csv
    output/ari_metrics.json
    Plots in visualizations/
4. Lint and test
    make lint
    make test
5. Clean outputs
    make clean
    make clean-all
All runs are logged under the experiment name "AIML Glossary Analysis".

Parameters, metrics, and artifacts are tracked automatically.

To view results, start the MLflow UI:
    mlflow ui --backend-store-uri experiments/mlruns
Then open http://127.0.0.1:5000 in your browser.

Outputs: Generate enriched glossary in Markdown/XHTML.

Graph clustering: Louvain algorithm groups terms by connectivity.

Semantic clustering: TF-IDF + KMeans groups terms by definition similarity.

Evaluation: Adjusted Rand Index compares graph vs semantic clusters.

Dashboard: ARI trend and bar charts visualize consistency across runs.


---

This version is complete, consistent with your updated scripts and Makefile, and beginner‑friendly with Quick Start instructions.
