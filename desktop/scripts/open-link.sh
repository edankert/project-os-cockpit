#!/usr/bin/env bash
# Open a page in the running cockpit window (ISS-0293).
#
#   desktop/scripts/open-link.sh your-health docs/design/README.md
#   desktop/scripts/open-link.sh your-health FEAT-0107
#   desktop/scripts/open-link.sh 'cockpit://your-health/docs/design/README.md'
#
# The project is a project id (what a [[project#ID]] link names) or the
# shell's workspace id. The target is a path under docs/ or a note ID, and
# may be left out to switch project only.
#
# Why a script and not `open cockpit://…`: macOS routes a URL scheme only to a
# packaged app bundle, and this shell runs from source as `electron .`, so no
# handler is registered. A second `electron .` is refused the single-instance
# lock, hands its argv to the running window through `second-instance`, and
# quits without starting anything.
#
# If the cockpit is not running, this starts it and the link is not opened:
# a first instance does not read its own argv.
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <project> [<target>]   or   $0 cockpit://<project>/<target>" >&2
  exit 2
fi

if [[ "$1" == cockpit://* ]]; then
  url="$1"
else
  url="cockpit://$1/${2:-}"
fi

desktop="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
electron="$desktop/node_modules/.bin/electron"
if [[ ! -x "$electron" ]]; then
  echo "open-link: $electron is missing; run npm install in $desktop" >&2
  exit 1
fi
if [[ ! -f "$desktop/dist/main.js" ]]; then
  echo "open-link: dist/main.js is missing; run npm run build in $desktop" >&2
  exit 1
fi

cd "$desktop"
"$electron" . "$url" >/dev/null 2>&1
echo "open-link: sent $url"
