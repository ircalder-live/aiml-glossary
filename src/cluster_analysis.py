# src/cluster_analysis.py

import json
from pathlib import Path
import networkx as nx
from typing import Dict, List


def build_graph(glossary_json: str, link_dict_json: str) -> nx.DiGraph:
    """
    Build a directed graph from glossary terms and link dictionary.

    This function is required by tests/test_cluster_analysis.py.
    It constructs a NetworkX DiGraph where:
    - Each glossary term becomes a node.
    - Each link_dict entry creates directed edges: src -> target.

    Parameters
    ----------
    glossary_json : str
        Path to a JSON file containing a list of glossary entries.
        Each entry must contain at least a "term" field.
    link_dict_json : str
        Path to a JSON file containing a mapping of term -> list of related terms.

    Returns
    -------
    nx.DiGraph
        A directed graph representing glossary relationships.
    """
    glossary_path = Path(glossary_json)
    link_dict_path = Path(link_dict_json)

    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    link_dict: Dict[str, List[str]] = json.loads(
        link_dict_path.read_text(encoding="utf-8")
    )

    G = nx.DiGraph()

    # Add nodes for each glossary term
    for entry in glossary:
        term = entry.get("term")
        if term:
            G.add_node(term)

    # Add directed edges from link dictionary
    for src, targets in link_dict.items():
        for tgt in targets:
            if src in G and tgt in G:
                G.add_edge(src, tgt)

    return G


# ---------------------------------------------------------------------------
# Additional clustering utilities (kept minimal and clean)
# ---------------------------------------------------------------------------


def compute_graph_stats(G: nx.DiGraph) -> Dict[str, int]:
    """
    Compute simple statistics for a glossary graph.

    Returns a dictionary with:
    - number of nodes
    - number of edges
    - number of isolated nodes
    """
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "isolated_nodes": len(list(nx.isolates(G))),
    }


def save_graph_gml(G: nx.DiGraph, output_path: str) -> None:
    """
    Save the graph to a GML file for visualization or downstream analysis.
    """
    nx.write_gml(G, output_path)
