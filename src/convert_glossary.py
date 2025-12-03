import os
import re
import json

def parse_glossary(md_file, json_file):
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split entries by headings (### Term)
    entries = re.split(r"^###\s+", content, flags=re.MULTILINE)[1:]
    glossary = []

    for entry in entries:
        lines = entry.strip().split("\n")
        term = lines[0].strip()

        def extract(pattern):
            match = re.search(pattern, entry, flags=re.MULTILINE)
            return match.group(1).strip() if match else ""

        # Use non-greedy patterns anchored to line breaks
        definition = extract(r"\*\*Definition:\*\*\s*(.+?)(?:\n|$)")
        tags_text = extract(r"\*\*Tags:\*\*\s*(.+?)(?:\n|$)")
        related_text = extract(r"\*\*Related Terms:\*\*\s*(.+?)(?:\n|$)")
        examples_text = extract(r"\*\*Examples:\*\*\s*(.+?)(?:\n|$)")
        source = extract(r"\*\*Source:\*\*\s*(.+?)(?:\n|$)")
        last_updated = extract(r"\*\*Last Updated:\*\*\s*(.+?)(?:\n|$)")

        # Robust splitting for tags, related terms, examples
        tags = re.split(r",\s*", tags_text.replace("`", "")) if tags_text else []
        related = re.split(r",\s*", related_text) if related_text else []
        examples = re.split(r";\s*|\n", examples_text) if examples_text else []

        glossary.append({
            "term": term,
            "definition": definition,
            "tags": [t.strip() for t in tags if t.strip()],
            "related_terms": [r.strip() for r in related if r.strip()],
            "examples": [e.strip() for e in examples if e.strip()],
            "source": source,
            "last_updated": last_updated
        })

    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(glossary, f, indent=2, ensure_ascii=False)

    print(f"Converted {len(glossary)} entries from {md_file} → {json_file}")

if __name__ == "__main__":
    md_input = os.path.join("output", "glossary.md")
    json_output = os.path.join("data", "aiml_glossary.json")
    parse_glossary(md_input, json_output)
