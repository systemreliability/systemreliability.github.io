#!/bin/bash
set -euo pipefail
[[ "$(uname -s)" == Darwin ]] || { echo "macOS only" >&2; exit 1; }
LABEL="info.dongkyu-lee.scholar"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "Removed weekly automation. Repository data, logs, and attempt history were preserved."
