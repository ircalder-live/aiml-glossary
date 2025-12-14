# src/coverage_report.py

from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parent.parent

def report_link_coverage(glossary, link_dict, output_dir: Path = REPO_ROOT / "output"):
    """
    Generate a simple coverage report: how many glossary terms have links.

    Parameters
    ----------
    glossary : list of dict
        Enriched glossary entries.
    link_dict : dict
        Dictionary mapping terms to linked terms.
    output_dir : Path
        Directory to write coverage report.
    """
    total_terms = len(glossary)

    # Count terms that have at least one link in the dictionary
    covered_terms = sum(
        1 for entry in glossary
        if link_dict.get(entry.get("term", ""), [])
    )

    coverage = covered_terms / total_terms if total_terms else 0.0

    report = {
        "total_terms": total_terms,
        "covered_terms": covered_terms,
        "coverage_percent": round(coverage * 100, 2)
    }

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / "coverage_report.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Coverage: {covered_terms}/{total_terms} terms ({report['coverage_percent']}%)")
    print(f"Coverage report written to {report_file}")
