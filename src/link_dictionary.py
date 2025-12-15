# src/link_dictionary.py
"""
Build a link dictionary for glossary terms.
Links are inferred by simple co-occurrence heuristics (e.g., term mentions in definitions).
Saves dictionary to output artifacts.
"""

import json
from src.utils import resolve_uri, load_glossary


def build_link_dictionary(glossary_json: str) -> None:
    """Build link dictionary using URIs for input/output."""
    glossary_dict = load_glossary(glossary_json)

    terms = list(glossary_dict.keys())
    link_dict = {term: [] for term in terms}

    # Simple heuristic: if a term appears in another term's definition, link them
    for term, definition in glossary_dict.items():
        for other in terms:
            if other != term and other.lower() in definition.lower():
                link_dict[term].append(other)

    # Save link dictionary
    link_dict_file = resolve_uri("output:link_dictionary.json")
    with open(link_dict_file, "w", encoding="utf-8") as f:
        json.dump(link_dict, f, indent=2)

    print(f"Link dictionary written to {link_dict_file}")


def main() -> None:
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 -m src.link_dictionary <glossary_json>")
        sys.exit(1)
    build_link_dictionary(sys.argv[1])


if __name__ == "__main__":
    main()
