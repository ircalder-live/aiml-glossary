# src/generate_outputs.py
"""
Generate outputs from glossary JSON into the given directory.
Creates CSV and JSON artifacts for downstream clustering and publishing.
Supports glossary JSON as either a dict {term: definition} or a list of {term, definition}.
"""

import json
from src.utils import resolve_uri


def generate(glossary_json: str, output_dir: str) -> None:
    """Generate outputs from glossary JSON into the given directory (URI-based)."""
    out_dir = resolve_uri(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    glossary_path = resolve_uri(glossary_json)
    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")

    # Load glossary
    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    # Normalize glossary into a dict
    if isinstance(glossary, dict):
        glossary_dict = glossary
    elif isinstance(glossary, list):
        glossary_dict = {entry["term"]: entry["definition"] for entry in glossary}
    else:
        raise TypeError(f"Unexpected glossary format: {type(glossary)}")

    # Save terms to CSV
    terms_file = out_dir / "terms.csv"
    with open(terms_file, "w", encoding="utf-8") as f:
        f.write("term,definition\n")
        for term, definition in glossary_dict.items():
            safe_def = definition.replace(",", ";")
            f.write(f"{term},{safe_def}\n")

    # Save glossary copy to JSON
    glossary_copy = out_dir / "glossary_copy.json"
    with open(glossary_copy, "w", encoding="utf-8") as f:
        json.dump(glossary_dict, f, indent=2)

    print(f"Terms written to {terms_file}")
    print(f"Glossary copy written to {glossary_copy}")


def main() -> None:
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 -m src.generate_outputs <glossary_json> <output_dir>")
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
