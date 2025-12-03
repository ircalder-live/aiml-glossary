#!/usr/bin/env python3
"""
validate_glossary.py

Validate AIML glossary data against glossary.schema.json using jsonschema.
Run this after adding new entries to catch errors early.
"""

import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

# Paths
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GLOSSARY_FILE = DATA_DIR / "aiml_glossary.json"
SCHEMA_FILE = DATA_DIR / "glossary.schema.json"

def main():
    try:
        # Load schema
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Load glossary data
        with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
            glossary = json.load(f)

        # Validate
        validate(instance=glossary, schema=schema)
        print("✅ Glossary data is valid against schema.")

    except ValidationError as e:
        print("❌ Validation error:")
        print(f"  Path: {'/'.join(map(str, e.path))}")
        print(f"  Message: {e.message}")
        sys.exit(1)

    except Exception as e:
        print("❌ Unexpected error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
