#!/bin/bash
# Install only. Does not make a Scholar request or run the job immediately.
set -euo pipefail
[[ "$(uname -s)" == Darwin ]] || { echo "macOS only" >&2; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="info.dongkyu-lee.scholar"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
HOUR=9
MINUTE=10
if [[ $# -ge 1 ]]; then HOUR="$1"; fi
if [[ $# -ge 2 ]]; then MINUTE="$2"; fi
PYTHON="$(command -v python3)"
"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
"$PYTHON" -m venv "$ROOT/.venv-scholar"
"$ROOT/.venv-scholar/bin/python" -m pip install -r "$ROOT/bin/requirements-scholar.txt"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs/PersonalScholarUpdater"
"$ROOT/.venv-scholar/bin/python" - "$ROOT" "$PLIST" "$HOUR" "$MINUTE" "$LABEL" <<'PY'
import os, pathlib, plistlib, sys, tempfile
root, target, hour, minute, label = sys.argv[1:]
hour, minute = int(hour), int(minute)
if not (0 <= hour <= 23 and 0 <= minute <= 59):
    raise SystemExit("Hour must be 0..23 and minute 0..59")
logs = pathlib.Path.home() / "Library/Logs/PersonalScholarUpdater"
job = {
    "Label": label,
    "ProgramArguments": [root + "/.venv-scholar/bin/python", root + "/bin/update_scholar_citations.py", "--repo", root, "--publish"],
    "WorkingDirectory": root,
    "StartCalendarInterval": {"Hour": hour, "Minute": minute},
    "RunAtLoad": False,
    "ProcessType": "Background",
    "StandardOutPath": str(logs / "stdout.log"),
    "StandardErrorPath": str(logs / "stderr.log"),
    "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin", "PYTHONUNBUFFERED": "1"},
}
fd, temporary = tempfile.mkstemp(dir=pathlib.Path(target).parent)
try:
    with os.fdopen(fd, "wb") as stream:
        plistlib.dump(job, stream)
    os.chmod(temporary, 0o600)
    os.replace(temporary, target)
finally:
    if os.path.exists(temporary):
        os.unlink(temporary)
PY
plutil -lint "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed $LABEL daily at $HOUR:$MINUTE in macOS local time."
echo "No initial fetch performed. Run the documented manual --publish check once."
