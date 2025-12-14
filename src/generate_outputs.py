# src/generate_outputs.py

from pathlib import Path
from src.link_dictionary import update_link_dictionary

REPO_ROOT = Path(__file__).resolve().parent.parent

def generate_outputs(
    glossary_file: Path = REPO_ROOT / "data" / "aiml_glossary.json",
    link_dict_file: Path = REPO_ROOT / "data" / "link_dictionary.json",
    template_dir: Path = REPO_ROOT / "templates",
    output_dir: Path = REPO_ROOT / "output"
):

    """
    Generate glossary outputs: update link dictionary, enrich entries,
    render templates, and report coverage.
    """
    glossary_file = Path(glossary_file)
    link_dict_file = Path(link_dict_file)
    template_dir = Path(template_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Update link dictionary ---
    print(f"▶ Updating link dictionary from {glossary_file} → {link_dict_file}")
    link_dict, entries = update_link_dictionary(
        glossary_file=glossary_file,
        link_dict_file=link_dict_file
    )

    # --- Step 2: Enrich glossary entries ---
    print("▶ Enriching glossary entries...")
    enriched = []
    for entry in entries:
        term = entry.get("term", "").strip()
        definition = entry.get("definition", "").strip()
        links = link_dict.get(term, [])
        enriched.append({
            "term": term,
            "definition": definition,
            "links": links
        })

    # --- Step 3: Render templates ---
    print(f"▶ Rendering templates into {output_dir}...")
    glossary_md = output_dir / "glossary.md"
    with open(glossary_md, "w", encoding="utf-8") as f:
        for e in enriched:
            f.write(f"### {e['term']}\n{e['definition']}\n\n")
            if e["links"]:
                f.write(f"Links: {', '.join(e['links'])}\n\n")

    # --- Step 4: Report coverage ---
    print("▶ Reporting link coverage...")
    covered = sum(1 for e in enriched if e["links"])
    total = len(enriched)
    print(f"Coverage: {covered}/{total} terms ({covered/total*100:.1f}%)")

    print(f"DEBUG: Returning glossary with {len(enriched)} entries and link_dict with {len(link_dict)} terms")
    return enriched, link_dict
