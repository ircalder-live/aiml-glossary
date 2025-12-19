# src/coverage_report.py
"""
Generate a coverage report of expected artifacts.
Checks whether each expected output/visualization file exists and saves a summary JSON.
Also validates glossary presence and normalization via load_glossary().
"""

import json
from src.utils import resolve_uri, load_glossary


EXPECTED_ARTIFACTS = [
    "data:aiml_glossary.json",
    "data:terms.csv",
    "data:glossary_copy.json",
    "data:link_dictionary.json",
    "data:enriched_glossary.json",
    "data:cluster_assignments.csv",
    "data:semantic_cluster_assignments.csv",
    "data:graph_stats.json",
    "data:ari_metrics.json",
    "data:coverage_report.json",
    "visualizations:glossary_clusters.png",
    "visualizations:semantic_clusters.png",
]


def generate_report() -> dict:
    """Generate coverage report using URIs for artifact paths and glossary normalization."""
    report = {}

    # Validate glossary presence and normalization
    try:
        glossary_dict = load_glossary("data:aiml_glossary.json")
        report["data:aiml_glossary.json"] = bool(glossary_dict)
    except Exception as e:
        report["data:aiml_glossary.json"] = f"Error: {e}"

    # Check other artifacts
    for uri in EXPECTED_ARTIFACTS:
        if uri == "data:aiml_glossary.json":
            continue  # already checked above
        path = resolve_uri(uri)
        report[uri] = path.exists()

    # Save report
    report_file = resolve_uri("data/coverage_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Console summary
    print("Coverage Report:")
    for uri, status in report.items():
        if status is True:
            marker = "✅"
        elif status is False:
            marker = "❌"
        else:
            marker = "⚠️"
        print(f"{marker} {uri} ({status})")

    print(f"\nCoverage report written to {report_file}")
    return report


def main() -> None:
    generate_report()


if __name__ == "__main__":
    main()
