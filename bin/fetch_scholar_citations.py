#!/usr/bin/env python3
"""Compatibility entry point: read cached data only; never contact Scholar."""
import argparse
import json
from pathlib import Path
import sys

from update_scholar_citations import AUTHOR_ID, load_existing, UpdateError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("author_id")
    parser.add_argument("publication_id")
    args = parser.parse_args()
    try:
        if args.author_id != AUTHOR_ID:
            raise UpdateError("Unknown profile")
        data = load_existing(Path(__file__).resolve().parents[1])
        key = args.publication_id
        full = key if ":" in key else AUTHOR_ID + ":" + key
        paper = data["papers"].get(full) or data["papers"].get(full.split(":", 1)[1])
        if paper is None:
            raise UpdateError("Publication not in local cache")
        print(json.dumps({"citations": paper["citations"]}))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
