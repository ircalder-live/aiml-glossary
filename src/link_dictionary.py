# src/link_dictionary.py

from pathlib import Path
import json
import re

REPO_ROOT = Path(__file__).resolve().parent.parent

# Simple synonym map: maps lowercase variants to canonical glossary terms
SYNONYM_MAP = {
    "neural nets": "Neural Network",
    "nn": "Neural Network",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "dl": "Deep Learning",
    # Add more as needed
}

def simple_stem(word: str) -> str:
    """Lightweight stemmer: strips common suffixes."""
    return re.sub(r'(ing|ed|es|s)$', '', word.lower())

def tokenize(text: str):
    """Split text into alphanumeric tokens."""
    return re.findall(r'\b\w+\b', text.lower())

def update_link_dictionary(
    glossary_file: Path = REPO_ROOT / "data" / "aiml_glossary.json",
    link_dict_file: Path = REPO_ROOT / "data" / "link_dictionary.json"
):
    """
    Build a link dictionary mapping each term to other terms mentioned in its definition.
    Adds phrase matching for multi-word terms and synonym expansion.
    Returns both the link_dict and the glossary entries.
    """
    glossary_file = Path(glossary_file)
    link_dict_file = Path(link_dict_file)

    if not glossary_file.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_file}")

    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    terms = {entry["term"].strip() for entry in glossary if "term" in entry}
    link_dict = {}

    for entry in glossary:
        term = entry.get("term", "").strip()
        definition = entry.get("definition", "").lower()
        links = []

        # --- Phrase matching for multi-word terms ---
        for candidate in terms:
            candidate_lower = candidate.lower()
            if candidate_lower in definition and candidate_lower != term.lower():
                links.append(candidate)

        # --- Synonym expansion ---
        for synonym, canonical in SYNONYM_MAP.items():
            if synonym in definition and canonical.lower() != term.lower():
                links.append(canonical)

        # --- Token-level matching with simple stemming ---
        tokens = [simple_stem(tok) for tok in tokenize(definition)]
        for candidate in terms:
            stemmed = simple_stem(candidate)
            if stemmed in tokens and candidate.lower() != term.lower():
                links.append(candidate)

        link_dict[term] = sorted(set(links))

    with open(link_dict_file, "w", encoding="utf-8") as f:
        json.dump(link_dict, f, indent=2)

    print(f"Link dictionary written to {link_dict_file} with {len(link_dict)} terms.")
    return link_dict, glossary
