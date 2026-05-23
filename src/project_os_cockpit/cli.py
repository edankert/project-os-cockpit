"""Tiny ``cockpit`` CLI for in-terminal agents (TASK-0049).

Designed to be called from the LLM CLI session running inside the
cockpit's embedded terminal. Discovers the cockpit's HTTP base URL via
the ``COCKPIT_URL`` env var (set by ``terminal.py`` when spawning
ttyd's shell). Commands POST to the cockpit server which then
broadcasts an SSE event to every open browser tab.

Example::

    cockpit focus FEAT-0006
    cockpit focus docs/features/cockpit/FEAT-0006-Cockpit-Layout.md
    cockpit focus /docs/changes/CHG-20260522-Foo.md

Subcommands are intentionally minimal in v1 (``focus`` only); ``pin``,
``toggle``, ``query`` etc. are reserved for follow-ups.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def _walk_up_for_discovery(start: Path) -> str:
    """Walk up from ``start`` looking for ``.cockpit/url`` — the file the
    cockpit server writes on startup so any-terminal CLIs can find it.

    Returns the URL string (without trailing slash) or ``""`` if no
    discovery file is found before reaching the filesystem root.
    """
    here = start.resolve()
    while True:
        candidate = here / ".cockpit" / "url"
        if candidate.is_file():
            try:
                return candidate.read_text(encoding="utf-8").strip().rstrip("/")
            except OSError:
                return ""
        parent = here.parent
        if parent == here:
            return ""
        here = parent


def _default_base_url() -> str:
    """Cockpit URL, discovered in priority order:

    1. ``COCKPIT_URL`` env (set automatically when the embedded ttyd
       spawns its shell).
    2. ``<ancestor>/.cockpit/url`` walking up from CWD (lets an LLM in
       any terminal under the project tree drive a running cockpit).
    """
    env = os.environ.get("COCKPIT_URL", "").strip().rstrip("/")
    if env:
        return env
    return _walk_up_for_discovery(Path.cwd())


def _post_json(base: str, path: str, body: dict) -> tuple[int, dict]:
    """POST JSON to the cockpit; return (status, parsed-body)."""
    if not base:
        print(
            "cockpit: no running cockpit found. Either:\n"
            "  - run this from inside a directory served by a cockpit "
            "(it writes .cockpit/url at startup), or\n"
            "  - set COCKPIT_URL=http://host:port explicitly.",
            file=sys.stderr,
        )
        return 0, {}
    url = base + path
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            raw = ""
        status = exc.code
    except urllib.error.URLError as exc:
        print(f"cockpit: cannot reach {url}: {exc.reason}", file=sys.stderr)
        return 0, {}
    try:
        parsed = json.loads(raw) if raw else {}
    except ValueError:
        parsed = {"raw": raw}
    return status, parsed


def cmd_focus(args: argparse.Namespace) -> int:
    base = args.cockpit_url or _default_base_url()
    status, body = _post_json(base, "/api/cockpit/focus", {"target": args.target})
    if status == 0:
        return 1
    if status >= 400 or not body.get("ok"):
        msg = body.get("error") or f"HTTP {status}"
        print(f"cockpit focus: {msg}", file=sys.stderr)
        return 1
    print(f"cockpit -> {body.get('url')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cockpit",
        description="Drive the project-os-cockpit window from inside the embedded terminal.",
    )
    parser.add_argument(
        "--cockpit-url",
        default=None,
        help="Override COCKPIT_URL env var (e.g. http://127.0.0.1:8770).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_focus = sub.add_parser(
        "focus",
        help="Navigate every open cockpit tab to a note (by ID, path, or URL).",
    )
    p_focus.add_argument(
        "target",
        help="Note ID (FEAT-0006), docs-rel path, or full URL (/docs/...).",
    )
    p_focus.set_defaults(func=cmd_focus)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
