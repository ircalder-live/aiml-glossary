# src/enrich_glossary.py
"""
Enrich glossary entries with metadata and save to output.
Adds diagnostic fields like definition length, character count, and link counts.
"""

import json
from src.utils import resolve_uri, load_glossary


def enrich_glossary(glossary_json: str, link_dict_json: str) -> None:
    """Enrich glossary entries with metadata and save to output (URI-based)."""
    glossary_dict = load_glossary(glossary_json)
    link_dict_path = resolve_uri(link_dict_json)

    if not link_dict_path.exists():
        raise FileNotFoundError(f"Link dictionary file not found: {link_dict_path}")

    # Load link dictionary
    with open(link_dict_path, "r", encoding="utf-8") as f:
        link_dict = json.load(f)

    enriched = {}
    for term, definition in glossary_dict.items():
        links = link_dict.get(term, [])
        enriched[term] = {
            "definition": definition,
            "length": len(definition.split()),
            "characters": len(definition),
            "link_count": len(links),
            "links": links,
        }

    # Save enriched glossary
    enriched_file = resolve_uri("output:enriched_glossary.json")
    with open(enriched_file, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)

    print(f"Enriched glossary written to {enriched_file}")


def main() -> None:
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 -m src.enrich_glossary <glossary_json> <link_dict_json>")
        sys.exit(1)
    enrich_glossary(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
