#!/usr/bin/env python3
"""Build the --content JSON for an inline single-file DevOps Agent asset.

Reads a text file (a system prompt or SKILL.md) and prints a JSON object of the
shape the Asset API expects for a single inline text file:

  { "file": { "path": "<path>", "body": { "text": "<file contents>" } } }

json.dumps handles all escaping (newlines, quotes, backslashes), so the output
is safe to pass to `aws devops-agent create-asset --content`.

Usage:
  python scripts/_asset_content.py <source-file> [asset-path]

  source-file  Path to the text file to embed (required).
  asset-path   Path to store the file under inside the asset. Defaults to the
               source file's base name (for example AGENT.md or SKILL.md).
"""

import json
import os
import sys


def main(argv):
    if len(argv) < 2:
        sys.stderr.write(
            "usage: python scripts/_asset_content.py <source-file> [asset-path]\n"
        )
        return 2
    source = argv[1]
    asset_path = argv[2] if len(argv) > 2 else os.path.basename(source)
    try:
        with open(source, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        sys.stderr.write("cannot read %s: %s\n" % (source, exc))
        return 1
    content = {"file": {"path": asset_path, "body": {"text": text}}}
    sys.stdout.write(json.dumps(content))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
