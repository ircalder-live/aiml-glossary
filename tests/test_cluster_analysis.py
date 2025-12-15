import os
import json
import pandas as pd
from src import cluster_analysis


def test_build_graph_creates_nodes_and_edges(tmp_path):
    """Verify that build_graph adds nodes and edges from glossary and link_dict."""
    glossary = [
        {"term": "AI", "related_terms": ["ML"]},
        {"term": "ML", "related_terms": []},
    ]
    link_dict = {"AI": ["ML"]}

    glossary_file = tmp_path / "glossary.json"
    link_dict_file = tmp_path / "links.json"

    glossary_file.write_text(json.dumps(glossary))
    link_dict_file.write_text(json.dumps(link_dict))

    G = cluster_analysis.build_graph(str(glossary_file), str(link_dict_file))

    # Assert nodes exist
    assert "AI" in G.nodes
    assert "ML" in G.nodes

    # Assert edge exists
    assert ("AI", "ML") in G.edges


def test_run_clustering_outputs_files(tmp_path):
    """Verify that run_clustering produces cluster assignments and visualization files."""
    glossary = [
        {"term": "AI", "related_terms": ["ML"]},
        {"term": "ML", "related_terms": []},
    ]
    link_dict = {"AI": ["ML"]}

    glossary_file = tmp_path / "glossary.json"
    link_dict_file = tmp_path / "links.json"

    glossary_file.write_text(json.dumps(glossary))
    link_dict_file.write_text(json.dumps(link_dict))

    # Change working directory to tmp_path so outputs go there
    cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        cluster_analysis.run_clustering(str(glossary_file), str(link_dict_file))

        # Check that output files exist
        assert os.path.exists("output/cluster_assignments.csv")
        assert os.path.exists("visualizations/glossary_clusters.png")

        # Check that cluster_assignments.csv has expected columns
        df = pd.read_csv("output/cluster_assignments.csv")
        assert {"term", "cluster_id"}.issubset(df.columns)
    finally:
        os.chdir(cwd)
