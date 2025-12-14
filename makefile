# AIML Glossary Workflow Makefile

PYTHON := python3

# Default target runs the full workflow
all: validate outputs cluster publish

# Validate glossary JSON against schema
validate:
	$(PYTHON) src/validate_glossary.py data/aiml_glossary.json data/glossary.schema.json

# Generate outputs (Markdown, HTML, etc.)
outputs:
	$(PYTHON) src/generate_outputs.py data/aiml_glossary.json outputs/

# Cluster glossary terms for analysis
cluster:
	$(PYTHON) src/cluster_terms.py

# Publish outputs (e.g. copy to docs/ or site/)
publish:
	$(PYTHON) src/publish_outputs.py outputs/ docs/

# Clean up generated files
clean:
	rm -rf outputs/* docs/*

# --- Developer workflow targets ---

# Install development dependencies
dev-install:
	pip install -r dev-requirements.txt

# Run linting
lint:
	$(PYTHON) -m ruff check src/ data/

# Run tests
test:
	$(PYTHON) -m pytest --maxfail=1 --disable-warnings -q

# Run coverage
coverage:
	$(PYTHON) -m pytest --cov=src --cov-report=term-missing
