import json
import pytest
from src import validate_glossary


def test_validate_glossary_valid_entry(tmp_path):
    """Ensure a well-formed glossary entry passes validation."""
    glossary = [
        {"term": "AI", "definition": "Artificial Intelligence", "related_terms": ["ML"]}
    ]
    glossary_file = tmp_path / "glossary.json"
    glossary_file.write_text(json.dumps(glossary))

    # Should not raise
    validate_glossary.validate_glossary(str(glossary_file))


def test_validate_glossary_malformed_entry(tmp_path):
    """Ensure malformed glossary entries raise a ValueError."""
    # Missing 'definition' field
    malformed_glossary = [{"term": "AI", "related_terms": ["ML"]}]
    glossary_file = tmp_path / "bad_glossary.json"
    glossary_file.write_text(json.dumps(malformed_glossary))

    with pytest.raises(ValueError):
        validate_glossary.validate_glossary(str(glossary_file))
