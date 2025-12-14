# src/publish_outputs.py

import shutil
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 src/publish_outputs.py <output_dir> <docs_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    docs_dir = Path(sys.argv[2])

    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    docs_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files from output_dir into docs_dir
    for file in output_dir.glob("*"):
        shutil.copy(file, docs_dir / file.name)
        print(f"Copied {file} → {docs_dir / file.name}")

if __name__ == "__main__":
    main()
