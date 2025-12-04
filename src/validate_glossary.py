import json


def validate_glossary(glossary_file: str) -> None:
    """
    Validate glossary entries in the given JSON file.

    Ensures each entry has required fields: 'term' and 'definition'.
    Raises ValueError if any entry is malformed.
    """
    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary = json.load(f)

    if not isinstance(glossary, list):
        raise ValueError("Glossary must be a list of entries")

    for entry in glossary:
        if not isinstance(entry, dict):
            raise ValueError("Each glossary entry must be a dictionary")

        # Required fields
        if "term" not in entry or not entry["term"]:
            raise ValueError("Glossary entry missing 'term'")
        if "definition" not in entry or not entry["definition"]:
            raise ValueError(f"Glossary entry '{entry.get('term')}' missing 'definition'")

        # Optional field validation
        if "related_terms" in entry and not isinstance(entry["related_terms"], list):
            raise ValueError(f"Glossary entry '{entry['term']}' has invalid 'related_terms'")

    # If no errors raised, glossary is valid
    return None


if __name__ == "__main__":
    # Example usage: validate a glossary file directly
    try:
        validate_glossary("data/aiml_glossary.json")
        print("Glossary validation passed.")
    except ValueError as e:
        print(f"Glossary validation failed: {e}")
