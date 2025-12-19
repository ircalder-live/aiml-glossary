# src/link_dictionary.py

import json
from pathlib import Path
import sys
import mlflow


def build_link_dictionary(glossary_json: str, output_file: str = "link_dictionary.json"):
    """
    Build a link dictionary mapping each term to related terms found in its definition text.
    - Resolves paths relative to repo root.
    - Iterates over dict-of-entries JSON.
    - Saves link dictionary to JSON.
    - Logs artifact into MLflow for contributor inspection.
    """

    # Resolve repo root (two levels up from this file: src/ -> repo root)
    repo_root = Path(__file__).resolve().parent.parent
    glossary_path = (repo_root / glossary_json).resolve()

    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")

    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_dict = json.load(f)

    # Collect all canonical terms
    terms = [entry.get("term", slug) for slug, entry in glossary_dict.items()]

    link_dict = {t: [] for t in terms}

    # Build dictionary by scanning definitions
    for slug, entry in glossary_dict.items():
        term = entry.get("term", slug)
        definition_text = entry.get("definition", "")

        for other in terms:
            if other != term and other.lower() in definition_text.lower():
                link_dict[term].append(other)

    # Save link dictionary to JSON
    output_path = (repo_root / output_file).resolve()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(link_dict, f, indent=2, ensure_ascii=False)

    print(f"✅ Link dictionary built: {output_path}")

    # Log artifact into MLflow
    try:
        with mlflow.start_run(run_name="link_dictionary", nested=True):
            mlflow.log_artifact(str(output_path), artifact_path="link_dictionary")
            mlflow.log_param("entries", len(glossary_dict))
            mlflow.log_param("linked_terms", sum(len(v) for v in link_dict.values()))
            print("📊 Link dictionary logged to MLflow")
    except Exception as e:
        print(f"⚠️ MLflow logging skipped: {e}")

    return link_dict


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.link_dictionary <glossary_json> [output_file]")
        sys.exit(1)

    glossary_json = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "link_dictionary.json"

    build_link_dictionary(glossary_json, output_file)
