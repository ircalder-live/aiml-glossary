AIML Glossary Project
=====================

![CI](https://github.com/ircalder-live/aiml-glossary/actions/workflows/ci.yml/badge.svg)
![Deploy](https://github.com/ircalder-live/aiml-glossary/actions/workflows/pages.yml/badge.svg)

📖 Overview
-----------
This project manages an AIML glossary as a reproducible workflow. It generates Markdown and XHTML outputs, enriches terms with hyperlinks, and analyzes glossary structure as a graph. The workflow is extended with MLflow logging and clustering analysis to track glossary evolution over time and visualize how terms cluster around key concepts.

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
