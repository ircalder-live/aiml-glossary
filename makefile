# Makefile — standardized module execution and explicit directories
.RECIPEPREFIX = >
MAKEFLAGS += --directory=$(CURDIR)

PY := python3
SRC := src
DATA := data
OUT := output
VIZ := visualizations
DOCS := docs
MLRUNS := experiments/mlruns

.PHONY: dirs
dirs:
>mkdir -p $(OUT) $(VIZ) $(DOCS) $(MLRUNS)

.PHONY: validate
validate: dirs
>$(PY) -m $(SRC).validate_glossary $(DATA)/aiml_glossary.json $(DATA)/glossary.schema.json

.PHONY: outputs
outputs: validate dirs
>$(PY) -m $(SRC).generate_outputs $(DATA)/aiml_glossary.json $(OUT)/

.PHONY: cluster
cluster: outputs dirs
>$(PY) -m $(SRC).cluster_terms

.PHONY: publish
publish: cluster dirs
>$(PY) -m $(SRC).publish_outputs $(OUT)/ $(DOCS)/

.PHONY: all
all: validate outputs cluster publish

# -----------------------------
# Linting & Formatting
# -----------------------------
.PHONY: lint
lint:
>$(PY) -m ruff check $(SRC)/ $(DATA)/

.PHONY: format
format:
>$(PY) -m ruff check --fix $(SRC)/ $(DATA)/
>$(PY) -m black $(SRC)/

# -----------------------------
# Testing
# -----------------------------
.PHONY: test
test:
>$(PY) -m pytest -q

.PHONY: check
check:
>pre-commit run --all-files
>$(PY) -m pytest -q

# -----------------------------
# Artifacts & Cleanup
# -----------------------------
.PHONY: artifacts
artifacts: dirs
>@echo "Artifacts ready in $(OUT) and $(VIZ). Upload in CI with actions/upload-artifact."

.PHONY: clean
clean:
>rm -rf $(OUT)/* $(VIZ)/* $(DOCS)/* $(MLRUNS)
>@echo "Cleaned build artifacts."

.PHONY: print-python
print-python:
>which python3
>python3 -c "import sys; print(sys.executable)"
>python3 -c "import src; print('src imported OK')"

.PHONY: debug-pytest
debug-pytest:
>$(PY) -m pytest --version
>$(PY) -m pytest --rootdir=.
