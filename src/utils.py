# src/utils.py
"""
Utility functions for URI-based resource resolution and glossary normalization.
Ensures reproducible workflows across local and CI/CD environments.
"""

import json
from pathlib import Path

# Assume repo layout: repo_root/{data,output,visualizations,src,notebooks}
REPO_ROOT = Path(__file__).resolve().parent.parent


def resolve_uri(uri: str) -> Path:
    """
    Resolve a logical URI like 'data:aiml_glossary.json' to a filesystem path.

    Prefixes:
      - data:           maps to REPO_ROOT/data
      - output:         maps to REPO_ROOT/output
      - visualizations: maps to REPO_ROOT/visualizations
    """
    if ":" not in uri:
        # Already a path string, return relative to repo root
        return REPO_ROOT / uri

    prefix, name = uri.split(":", 1)
    if prefix == "data":
        return REPO_ROOT / "data" / name
    elif prefix == "output":
        return REPO_ROOT / "output" / name
    elif prefix == "visualizations":
        return REPO_ROOT / "visualizations" / name
    else:
        raise ValueError(f"Unknown URI prefix: {prefix}")


def load_glossary(uri: str) -> dict:
    """
    Load glossary JSON from a URI and normalize into a dict {term: definition}.

    Supports two formats:
      - Dict: {"AI": "Artificial Intelligence", "ML": "Machine Learning"}
      - List: [{"term": "AI", "definition": "Artificial Intelligence"}, ...]

    Returns:
      dict mapping term -> definition
    """
    glossary_path = resolve_uri(uri)
    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")

    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    if isinstance(glossary, dict):
        return glossary
    elif isinstance(glossary, list):
        return {entry["term"]: entry["definition"] for entry in glossary}
    else:
        raise TypeError(f"Unexpected glossary format: {type(glossary)}")
