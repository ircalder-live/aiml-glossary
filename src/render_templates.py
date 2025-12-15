# src/render_templates.py

from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def render_templates(glossary, template_dir: Path, output_dir: Path):
    """
    Render glossary outputs (Markdown, XHTML) using Jinja2 templates.

    Parameters
    ----------
    glossary : list of dict
        Enriched glossary entries.
    template_dir : Path
        Directory containing Jinja2 templates.
    output_dir : Path
        Directory to write rendered outputs.
    """
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Render Markdown
    md_template = env.get_template("glossary.md.j2")
    md_output = md_template.render(entries=glossary)
    (output_dir / "glossary.md").write_text(md_output, encoding="utf-8")

    # Render XHTML
    xhtml_template = env.get_template("glossary.xhtml.j2")
    xhtml_output = xhtml_template.render(entries=glossary)
    (output_dir / "glossary.xhtml").write_text(xhtml_output, encoding="utf-8")
