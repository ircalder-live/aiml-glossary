# src/convert_glossary.py

from pathlib import Path
import json


def convert_glossary(
    markdown_file: Path, json_file: Path = Path("output/glossary_converted.json")
):
    """
    Convert glossary Markdown back into JSON format.

    Parameters
    ----------
    markdown_file : Path
        Path to the glossary Markdown file.
    json_file : Path, optional
        Path to write the converted glossary JSON file.
        Defaults to 'output/glossary_converted.json'.

    Returns
    -------
    list of dict
        Parsed glossary entries.
    """
    markdown_file = Path(markdown_file)
    json_file = Path(json_file)

    # --- Safety check: refuse to overwrite source glossary ---
    source_file = Path("data/aiml_glossary.json").resolve()
    if json_file.resolve() == source_file:
        raise ValueError(
            f"Refusing to overwrite source glossary file: {json_file}\n"
            "Please choose a different output path (e.g. output/glossary_converted.json)."
        )

    if not markdown_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    text = markdown_file.read_text(encoding="utf-8")

    # Very simple parser: assume "Term: Definition" per line
    entries = []
    for line in text.splitlines():
        if ":" in line:
            term, definition = line.split(":", 1)
            entries.append({"term": term.strip(), "definition": definition.strip()})

    # Ensure directory exists
    json_file.parent.mkdir(parents=True, exist_ok=True)

    # Write JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(entries)} entries from Markdown → JSON at {json_file}")
    return entries
