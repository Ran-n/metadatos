#!/usr/bin/env python3
# -----------------------------------------------------------------------------
"""
Authors: Ran# <ran.hash@proton.me>
Created: 2026/03/17 00:00:00.000000
Revised: 2026/03/17 00:00:00.000000
"""
# -----------------------------------------------------------------------------
# Generates the samples/ folder with one file of each supported type,
# then stamps each with a metadata header using metadatos.

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SAMPLES = HERE / "samples"
METADATOS = HERE / "main.py"

SAMPLES_CONTENT = {
    "sample.py": (
        "def greet(name: str) -> str:\n"
        '    return f"Hello, {name}!"\n'
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        '    print(greet("world"))\n'
    ),
    "sample.sh": 'echo "Hello, world!"\n',
    "sample.rs": 'fn main() {\n    println!("Hello, world!");\n}\n',
    "sample.md": "# Sample Document\n\nThis is an example Markdown file with metadatos metadata.\n",
}


def main():
    SAMPLES.mkdir(exist_ok=True)

    for filename, body in SAMPLES_CONTENT.items():
        path = SAMPLES / filename
        path.write_text(body, encoding="utf-8")
        subprocess.run([sys.executable, str(METADATOS), "-c", str(path)], check=True)
        print(f"created {path.relative_to(HERE)}")


if __name__ == "__main__":
    main()
