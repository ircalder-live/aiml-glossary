# src/enrich_glossary.py

def enrich_glossary(entries, link_dict):
    """
    Enrich glossary entries with link anchors.

    Parameters
    ----------
    entries : list of dict
        Glossary entries with 'term' and 'definition'.
    link_dict : dict
        Dictionary mapping terms to anchors.

    Returns
    -------
    list of dict
        Enriched glossary entries with 'anchor' field added.
    """
    enriched = []
    for entry in entries:
        term = entry.get("term")
        if term and term in link_dict:
            entry["anchor"] = link_dict[term]
        enriched.append(entry)
    return enriched
