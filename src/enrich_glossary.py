# src/enrich_glossary.py

import json
from pathlib import Path
import sys
import mlflow


def enrich_glossary(
    glossary_json: str,
    link_dict_json: str,
    output_file: str = "data/enriched_glossary.json",
):
    """
    Enrich glossary entries with related terms from the link dictionary.
    - Resolves paths relative to repo root.
    - Iterates over dict-of-entries JSON.
    - Adds 'linked_terms' field to each entry.
    - Saves enriched glossary to JSON (default: data/enriched_glossary.json).
    - Logs artifact into MLflow for contributor inspection.
    """

    # Resolve repo root (two levels up from this file: src/ -> repo root)
    repo_root = Path(__file__).resolve().parent.parent
    glossary_path = (repo_root / glossary_json).resolve()
    link_dict_path = (repo_root / link_dict_json).resolve()
    output_path = (repo_root / output_file).resolve()

    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")
    if not link_dict_path.exists():
        raise FileNotFoundError(f"Link dictionary file not found: {link_dict_path}")

    # Load glossary
    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_dict = json.load(f)

    # Load link dictionary
    with open(link_dict_path, "r", encoding="utf-8") as f:
        link_dict = json.load(f)

    # Enrich glossary entries
    for slug, entry in glossary_dict.items():
        term = entry.get("term", slug)
        linked_terms = link_dict.get(term, [])
        entry["linked_terms"] = linked_terms

    # Save enriched glossary
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(glossary_dict, f, indent=2, ensure_ascii=False)

    print(f"✅ Enriched glossary saved: {output_path}")

    # Log artifact into MLflow
    try:
        with mlflow.start_run(run_name="enrich_glossary", nested=True):
            mlflow.log_artifact(str(output_path), artifact_path="enriched_glossary")
            mlflow.log_param("entries", len(glossary_dict))
            print("📊 Enriched glossary logged to MLflow")
    except Exception as e:
        print(f"⚠️ MLflow logging skipped: {e}")

    return glossary_dict


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python -m src.enrich_glossary <glossary_json> <link_dict_json> [output_file]"
        )
        sys.exit(1)

    glossary_json = sys.argv[1]
    link_dict_json = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "data/enriched_glossary.json"

    enrich_glossary(glossary_json, link_dict_json, output_file)
