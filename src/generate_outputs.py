# src/generate_outputs.py

import json
from pathlib import Path
import sys


def generate(glossary_json: str = "data/aiml_glossary.json", output_dir: str = "data"):
    """
    Generate richer outputs from the glossary JSON.
    - Resolves paths relative to the repo root.
    - Reads glossary JSON (dict-of-entries keyed by slug).
    - Writes a CSV with slug, term, definition, tags, related_terms, examples, source, last_updated.
    - Writes a copy of the glossary to JSON in the output directory.
    - Defaults to writing into data/ as canonical sources.
    """

    repo_root = Path(__file__).resolve().parent.parent
    glossary_path = (repo_root / glossary_json).resolve()
    output_path = (repo_root / output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    if not glossary_path.exists():
        raise FileNotFoundError(f"Glossary file not found: {glossary_path}")

    with open(glossary_path, "r", encoding="utf-8") as f:
        glossary_dict = json.load(f)

    # Canonical filenames
    csv_file = output_path / "terms.csv"
    json_file = output_path / "glossary_copy.json"

    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(
            "slug,term,definition,tags,related_terms,examples,source,last_updated\n"
        )
        for slug, entry in glossary_dict.items():
            term = entry.get("term", slug)
            definition = entry.get("definition", "")
            tags = ";".join(entry.get("tags", []))
            related_terms = ";".join(entry.get("related_terms", []))
            examples = ";".join(entry.get("examples", []))
            source = entry.get("source", "")
            last_updated = entry.get("last_updated", "")
            safe_def = definition.replace(",", ";")
            f.write(
                f"{slug},{term},{safe_def},{tags},{related_terms},{examples},{source},{last_updated}\n"
            )

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(glossary_dict, f, indent=2, ensure_ascii=False)

    print(f"✅ Outputs generated: {csv_file}, {json_file}")


def generate_report(output_file: str = "data/coverage_report.json"):
    """
    Generate a coverage report for glossary artifacts and visualizations.
    - Checks data/ for JSON/CSV canonical artifacts.
    - Checks visualizations/ for plots.
    - Saves JSON summary and Markdown summary.
    - Prints grouped coverage metrics.
    """

    repo_root = Path(__file__).resolve().parent.parent

    # Expected artifacts
    data_files = [
        repo_root / "data/aiml_glossary.json",
        repo_root / "data/terms.csv",
        repo_root / "data/glossary_copy.json",
        repo_root / "data/link_dictionary.json",
        repo_root / "data/enriched_glossary.json",
        repo_root / "data/cluster_assignments.csv",
        repo_root / "data/semantic_cluster_assignments.csv",
        repo_root / "data/graph_stats.json",
        repo_root / "data/ari_metrics.json",
        repo_root / "data/coverage_report.json",
    ]
    viz_files = [
        repo_root / "visualizations/glossary_clusters.png",
        repo_root / "visualizations/semantic_clusters.png",
    ]

    # Build coverage dict
    coverage = {str(path): path.exists() for path in data_files + viz_files}

    # Always write JSON to canonical location
    output_path = (repo_root / "data/coverage_report.json").resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2)

    # Print grouped report
    print("Coverage Report:")

    def print_group(name, files):
        present = sum(1 for p in files if coverage[str(p)])
        total = len(files)
        print(f"\n{name} ({present}/{total} present = {present/total:.0%})")
        for p in files:
            status = "✅" if coverage[str(p)] else "❌"
            print(f"{status} {p.name} ({coverage[str(p)]})")

    print_group("Data artifacts", data_files)
    print_group("Visualizations", viz_files)

    # Overall coverage
    overall_present = sum(1 for v in coverage.values() if v)
    overall_total = len(coverage)
    print(
        f"\nOverall coverage: {overall_present}/{overall_total} files = {overall_present/overall_total:.0%}"
    )
    print(f"Coverage report written to {output_path}")

    # --- Write Markdown summary ---
    md_path = repo_root / "data/coverage_report.md"
    lines = []
    lines.append("# ✅ Coverage Summary\n")
    lines.append(
        "This report shows the presence and status of all canonical artifacts.\n\n"
    )

    # Data artifacts table
    lines.append("## 📁 Data Artifacts\n")
    lines.append("| File | Status |\n|------|--------|\n")
    for p in data_files:
        status = "✅ Present" if coverage[str(p)] else "❌ Missing"
        lines.append(f"| `{p.relative_to(repo_root)}` | {status} |\n")

    # Visualizations table
    lines.append("\n## 🖼️ Visualizations\n")
    lines.append("| File | Status |\n|------|--------|\n")
    for p in viz_files:
        status = "✅ Present" if coverage[str(p)] else "❌ Missing"
        lines.append(f"| `{p.relative_to(repo_root)}` | {status} |\n")

    # Overall summary
    lines.append("\n## 📊 Overall Coverage\n")
    lines.append(f"**✅ {overall_present} / {overall_total} artifacts present**\n")

    md_path.write_text("".join(lines), encoding="utf-8")
    print(f"Markdown coverage summary written to {md_path}")

    return coverage


if __name__ == "__main__":
    # Allow defaults so contributors can just run without args
    if len(sys.argv) == 1:
        generate()
        generate_report()  # always write to data/
    elif len(sys.argv) == 3:
        glossary_json = sys.argv[1]
        output_dir = sys.argv[2]
        generate(glossary_json, output_dir)
        generate_report()  # always write to data/
    else:
        print("Usage: python -m src.generate_outputs [<glossary_json> <output_dir>]")
        sys.exit(1)
