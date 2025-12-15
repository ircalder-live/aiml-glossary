# src/publish_outputs.py
"""
Publish generated outputs by copying them into the docs directory.
Intended for CI/CD integration and contributor visibility.
"""

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "output"
DOCS_DIR = REPO_ROOT / "docs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def publish_outputs(output_dir: Path = OUTPUT_DIR, docs_dir: Path = DOCS_DIR) -> None:
    """Copy generated outputs into the docs directory for publishing."""
    if not output_dir.exists():
        print(f"❌ Output directory not found: {output_dir}")
        sys.exit(1)

    for item in output_dir.iterdir():
        dest = docs_dir / item.name
        if item.is_file():
            shutil.copy(item, dest)
            print(f"Copied {item} → {dest}")
        elif item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            print(f"Copied directory {item} → {dest}")

    print(f"✅ Outputs published to {docs_dir}")


def main() -> None:
    """Entry point for CLI execution."""
    publish_outputs()


if __name__ == "__main__":
    main()
