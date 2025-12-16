# tests/test_validate_glossary.py
"""
Unit tests for glossary validation.
Ensures glossary JSON structure and link dictionary integrity.
"""

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def load_json(path: Path) -> dict:
    """Helper to load JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_glossary_exists() -> None:
    """Glossary JSON file should exist and be non-empty."""
    glossary_file = DATA_DIR / "aiml_glossary.json"
    assert glossary_file.exists(), "Glossary file missing"
    glossary = load_json(glossary_file)
    assert isinstance(glossary, dict), "Glossary should be a dict"
    assert glossary, "Glossary should not be empty"


def test_link_dictionary_exists() -> None:
    """Link dictionary JSON file should exist and be non-empty."""
    link_dict_file = DATA_DIR / "link_dictionary.json"
    assert link_dict_file.exists(), "Link dictionary file missing"
    link_dict = load_json(link_dict_file)
    assert isinstance(link_dict, dict), "Link dictionary should be a dict"
    assert link_dict, "Link dictionary should not be empty"


def test_terms_have_definitions() -> None:
    """Every glossary term should have a non-empty definition string."""
    glossary_file = DATA_DIR / "aiml_glossary.json"
    glossary = load_json(glossary_file)
    for term, definition in glossary.items():
        assert isinstance(definition, str), f"Definition for {term} should be a string"
        assert definition.strip(), f"Definition for {term} should not be empty"


def test_links_reference_existing_terms() -> None:
    """All links in link dictionary should reference valid glossary terms."""
    glossary_file = DATA_DIR / "aiml_glossary.json"
    link_dict_file = DATA_DIR / "link_dictionary.json"
    glossary = load_json(glossary_file)
    link_dict = load_json(link_dict_file)

    terms = set(glossary.keys())
    for term, links in link_dict.items():
        for link in links:
            assert link in terms, f"Link {link} in {term} not found in glossary"
