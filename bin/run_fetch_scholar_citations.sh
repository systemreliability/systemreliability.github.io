#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/.venv-scholar/bin/python" "$ROOT/bin/fetch_scholar_citations.py" "$@"
