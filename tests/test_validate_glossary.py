"""
Validation tests for the AIML glossary JSON file.

These tests enforce the canonical schema:
- The glossary file is a dict keyed by term slug.
- Each value is a dict containing at least a non-empty "definition" string.
- Optional metadata fields (id, examples, tags, etc.) are also validated.
"""

import json
from pathlib import Path

DATA_DIR = Path("data")
GLOSSARY_FILE = DATA_DIR / "aiml_glossary.json"


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def test_glossary_exists() -> None:
    """Glossary JSON file should exist and be non-empty dict."""
    assert GLOSSARY_FILE.exists(), "Glossary file missing"
    glossary = load_json(GLOSSARY_FILE)
    assert isinstance(glossary, dict), "Glossary should be a dict"
    assert glossary, "Glossary dict should not be empty"


def test_terms_have_definitions() -> None:
    """Every glossary entry should have a non-empty definition string."""
    glossary = load_json(GLOSSARY_FILE)
    for term, entry in glossary.items():
        assert isinstance(entry, dict), f"{term} should be a dict entry"
        definition = entry.get("definition")
        assert isinstance(definition, str), f"Definition for {term} should be a string"
        assert definition.strip(), f"Definition for {term} should not be empty"


def test_ids_are_unique() -> None:
    """If entries have 'id' fields, they should be unique."""
    glossary = load_json(GLOSSARY_FILE)
    ids = [
        entry.get("id") for entry in glossary.values() if entry.get("id") is not None
    ]
    assert len(ids) == len(set(ids)), "Duplicate IDs found in glossary"


def test_optional_metadata_types() -> None:
    """Optional metadata fields should have expected types."""
    glossary = load_json(GLOSSARY_FILE)
    for term, entry in glossary.items():
        if "examples" in entry:
            assert isinstance(
                entry["examples"], list
            ), f"Examples for {term} should be a list"
        if "tags" in entry:
            assert isinstance(entry["tags"], list), f"Tags for {term} should be a list"
        if "related_terms" in entry:
            assert isinstance(
                entry["related_terms"], list
            ), f"Related terms for {term} should be a list"
        if "last_updated" in entry:
            assert isinstance(
                entry["last_updated"], str
            ), f"last_updated for {term} should be a string"
