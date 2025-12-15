# tests/test_cluster_analysis.py

import json
import src.cluster_analysis as cluster_analysis


def test_build_graph_creates_nodes_and_edges(tmp_path):
    glossary = [
        {"term": "AI", "definition": "Artificial Intelligence"},
        {"term": "ML", "definition": "Machine Learning"},
    ]
    link_dict = {"AI": ["ML"]}

    glossary_file = tmp_path / "glossary.json"
    link_dict_file = tmp_path / "links.json"

    glossary_file.write_text(json.dumps(glossary))
    link_dict_file.write_text(json.dumps(link_dict))

    G = cluster_analysis.build_graph(str(glossary_file), str(link_dict_file))
    assert "AI" in G.nodes
    assert "ML" in G.nodes
    assert ("AI", "ML") in G.edges


def test_run_clustering_creates_artifacts(tmp_path):
    """Verify that run_clustering writes assignments, stats, and visualization."""

    glossary = {
        "AI": "Artificial Intelligence",
        "ML": "Machine Learning",
    }
    link_dict = {"AI": ["ML"]}

    glossary_file = tmp_path / "glossary.json"
    link_dict_file = tmp_path / "links.json"

    glossary_file.write_text(json.dumps(glossary))
    link_dict_file.write_text(json.dumps(link_dict))

    assignments_path = tmp_path / "cluster_assignments.csv"
    stats_path = tmp_path / "graph_stats.json"
    viz_path = tmp_path / "glossary_clusters.png"

    G = cluster_analysis.run_clustering(
        str(glossary_file),
        str(link_dict_file),
        assignments_path=str(assignments_path),
        stats_path=str(stats_path),
        viz_path=str(viz_path),
    )

    # Graph should contain expected nodes and edge
    assert "AI" in G.nodes
    assert "ML" in G.nodes
    assert ("AI", "ML") in G.edges

    # Artifacts should exist
    assert assignments_path.exists()
    assert stats_path.exists()
    assert viz_path.exists()
