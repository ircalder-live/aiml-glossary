import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# --- Helpers ---
def _safe_anchor(s: str) -> str:
    s = (s or "").strip()
    return "#" + "_".join(s.split())

def _extract_entries(glossary_data):
    if isinstance(glossary_data, list):
        return glossary_data
    if isinstance(glossary_data, dict):
        for key in ("glossary", "entries", "items"):
            if key in glossary_data and isinstance(glossary_data[key], list):
                return glossary_data[key]
    if isinstance(glossary_data, dict):
        possible_list = []
        for k, v in glossary_data.items():
            if isinstance(v, dict):
                v.setdefault("term", k)
                possible_list.append(v)
        if possible_list:
            return possible_list
    raise ValueError("Unable to locate entries list in aiml_glossary.json")

def _normalize_term(entry: dict):
    if not isinstance(entry, dict):
        return None
    for key in ("term", "Term", "name", "title"):
        if key in entry and isinstance(entry[key], str) and entry[key].strip():
            entry["term"] = entry[key].strip()
            return entry["term"]
    return None

# --- Step 1: Update link dictionary ---
def update_link_dictionary(glossary_file="data/aiml_glossary.json",
                           link_dict_file="data/link_dictionary.json",
                           output_file="data/link_dictionary.json"):
    with open(glossary_file, "r", encoding="utf-8") as f:
        glossary_data = json.load(f)

    entries = _extract_entries(glossary_data)

    if os.path.exists(link_dict_file):
        with open(link_dict_file, "r", encoding="utf-8") as f:
            link_dict = json.load(f)
    else:
        link_dict = {}

    skipped = []
    added = 0

    for entry in entries:
        term = _normalize_term(entry)
        if not term:
            skipped.append(entry)
            continue
        if term not in link_dict or not isinstance(link_dict[term], str) or not link_dict[term].strip():
            link_dict[term] = _safe_anchor(term)
            added += 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(link_dict, f, indent=2, ensure_ascii=False)

    if skipped:
        print(f"Note: {len(skipped)} entries lacked a usable 'term' and were skipped when updating anchors.")

    return link_dict, entries

# --- Step 2: Enrich glossary with links ---
def enrich_glossary(entries, link_dict):
    enriched = []
    for entry in entries:
        term = _normalize_term(entry)
        if not term:
            continue

        enriched_tags = []
        for tag in entry.get("tags", []):
            if isinstance(tag, dict):
                label = tag.get("label", "")
                url = tag.get("url", "")
            else:
                label = str(tag).strip()
                url = link_dict.get(label, _safe_anchor(label))
            enriched_tags.append({"label": label, "url": url})
        entry["tags"] = enriched_tags

        enriched_related = []
        for rel in entry.get("related_terms", []):
            if isinstance(rel, dict):
                label = rel.get("label", "")
                url = rel.get("url", "")
            else:
                label = str(rel).strip()
                url = link_dict.get(label, _safe_anchor(label))
            enriched_related.append({"label": label, "url": url})
        entry["related_terms"] = enriched_related

        enriched.append(entry)
    return enriched

# --- Step 3: Render templates ---
def render_templates(glossary, template_dir="templates", output_dir="output"):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xhtml", "xml"])
    )

    md_template = env.get_template("glossary.md.j2")
    html_template = env.get_template("glossary.xhtml.j2")

    os.makedirs(output_dir, exist_ok=True)

    md_output = md_template.render(glossary=glossary)
    with open(os.path.join(output_dir, "glossary.md"), "w", encoding="utf-8") as f:
        f.write(md_output)

    html_output = html_template.render(glossary=glossary)
    with open(os.path.join(output_dir, "glossary.xhtml"), "w", encoding="utf-8") as f:
        f.write(html_output)

    print("Markdown and XHTML generated in", output_dir)

# --- Step 4: Console + file report for link coverage ---
def report_link_coverage(link_dict, output_dir="output"):
    total_terms = len(link_dict)
    external_urls = sum(1 for url in link_dict.values() if isinstance(url, str) and not url.startswith("#"))
    internal_only = total_terms - external_urls
    coverage_pct = (external_urls / total_terms * 100) if total_terms > 0 else 0

    report_lines = [
        "📊 Link Coverage Report",
        f" - Total terms: {total_terms}",
        f" - Terms with external URLs: {external_urls}",
        f" - Terms with only internal anchors: {internal_only}",
        f" - External coverage: {coverage_pct:.1f}%"
    ]

    print("\n" + "\n".join(report_lines))

    if internal_only > 0:
        print("\n⚠️ Terms without external URLs (currently only internal anchors):")
        for term, url in link_dict.items():
            if isinstance(url, str) and url.startswith("#"):
                print(f" - {term}")
        print("\nYou may want to enrich these with external references in link_dictionary.json.")
    else:
        print("\n✅ All terms have external URLs defined.")

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "coverage_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

# --- Step 5: Orchestrate workflow ---
if __name__ == "__main__":
    glossary_file = os.path.join("data", "aiml_glossary.json")
    link_dict_file = os.path.join("data", "link_dictionary.json")

    link_dict, entries = update_link_dictionary(glossary_file, link_dict_file)

    glossary = enrich_glossary(entries, link_dict)

    render_templates(glossary)

    report_link_coverage(link_dict)
