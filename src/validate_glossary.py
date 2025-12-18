# src/validate_glossary.py

import json
from pathlib import Path
import sys


def validate_glossary(glossary_file: Path, schema_file: Path = None):
    """
    Validate the glossary JSON file.
    Ensures each entry has required fields: 'term' and 'definition'.
    Raises ValueError if validation fails.
    """
    glossary_file = Path(glossary_file)

    if not glossary_file.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_file}")

    with open(glossary_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both dict-of-entries and list-of-entries formats
    if isinstance(data, dict):
        glossary_entries = data.values()
    elif isinstance(data, list):
        glossary_entries = data
    else:
        raise ValueError("Glossary JSON must be a dict or list")

    errors = []
    for i, entry in enumerate(glossary_entries, start=1):
        if "term" not in entry:
            errors.append(f"Entry {i} missing 'term'")
        if "definition" not in entry:
            errors.append(f"Entry {i} missing 'definition'")

    if errors:
        print("❌ Validation failed:")
        for e in errors:
            print(" -", e)
        raise ValueError("Glossary validation failed")

    print("✅ Glossary validation passed")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 src/validate_glossary.py <glossary_file> [schema_file]")
        sys.exit(1)

    glossary_file = Path(sys.argv[1])
    schema_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        validate_glossary(glossary_file, schema_file)
    except Exception as e:
        print(f"Validation error: {e}")
        sys.exit(1)
