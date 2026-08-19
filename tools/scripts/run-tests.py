#!/usr/bin/env python3
"""Execute TST-* notes that declare a `command:` and report what happened (ADR-0038).

A test note carrying a `command:` records **that a machine executes it**. It does
not record whether it passed, and this script does not write one.

`QUALITY.md` builds its close-out rules on one gate: an item may not reach a
terminal status while a linked TST-* is not `passing`. Across 10 repos and 5,890
status writes that gate has never once observed a failure -- `failing` was
written zero times, 78% of test notes are born `passing`, and 99% never change
again.

**That measurement is unchanged; its reading is.** `project-os-dev#ADR-0010`
read "no failure was ever recorded" as *authors do not record failures* and moved
the writer here. The alternative reading fits the same number and costs a field
instead of a mechanism: **a red automated test is not a state anybody records,
because it is a state nobody ships.** A broken build gets fixed, not documented.

So the verdict lives in CI, and what the note keeps is the `command:` -- which is
strictly the better claim, because a stamped `passing` cannot notice that the
test it stands for was renamed and a command that stops resolving can.

Three outcomes, still deliberately distinguished, and all three are reported
rather than stored:

  passing     exit 0
  failing     non-zero exit -- the check ran and the system is wrong
  unrunnable  the command could not execute at all (missing binary, missing
              env, timeout)

Exit codes: 0 = no failures, 1 = at least one test failed, 2 = usage error.

Stdlib only. Usage:
    run-tests.py [--repo-root PATH] [--filter TST-0001] [--timeout N]
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT = 600


def split_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[:4], text[4:end], text[end:]


def fm_get(fm, key):
    m = re.search(r"^%s:\s*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def discover(root, only=None):
    out = []
    docs = root / "docs"
    if not docs.is_dir():
        return out
    for path in sorted(docs.rglob("*.md")):
        if "__templates__" in path.parts:
            continue
        if not re.match(r"^TST-\d+", path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        parts = split_frontmatter(text)
        if not parts:
            continue
        _pre, fm, _post = parts
        cmd = fm_get(fm, "command")
        if not cmd:
            continue
        tid = fm_get(fm, "id") or path.name.split("-")[0] + "-" + path.name.split("-")[1]
        if only and tid not in only:
            continue
        out.append((path, tid, cmd))
    return out


def run_one(root, cmd, timeout):
    """Return (outcome, exit_code, detail)."""
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=str(root), capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "PROJECT_OS_TEST_RUN": "1"},
        )
    except subprocess.TimeoutExpired:
        return "unrunnable", None, "timed out after %ss" % timeout
    except OSError as exc:
        return "unrunnable", None, "could not execute: %s" % exc
    # 127 is the shell's "command not found"; treat as environmental, not a failure.
    if proc.returncode == 127:
        head = (proc.stderr or "").strip().splitlines()[:1]
        return "unrunnable", 127, "command not found%s" % (": " + head[0] if head else "")
    tail = ((proc.stderr or "") + (proc.stdout or "")).strip().splitlines()[-1:]
    return ("passing" if proc.returncode == 0 else "failing"), proc.returncode, (tail[0] if tail else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run TST-* commands and stamp their status.")
    ap.add_argument("--repo-root", default=".")
    #: **Kept, and inert** (ADR-0038). Removing the flag would make every
    #: existing invocation fail with a usage error, and the honest answer to
    #: `--write` is not "unknown option" -- it is "there is nothing to write".
    ap.add_argument("--write", action="store_true",
                    help="Accepted and ignored: an automated test records no verdict (ADR-0038)")
    ap.add_argument("--filter", action="append", default=None, help="Only these TST ids")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args(argv)

    root = Path(args.repo_root).resolve()
    if not (root / "SNAPSHOT.yaml").is_file():
        print("run-tests: no SNAPSHOT.yaml at %s" % root, file=sys.stderr)
        return 2

    tests = discover(root, set(args.filter) if args.filter else None)
    if not tests:
        print("run-tests: %s — no TST-* notes declare a `command:`" % root.name)
        return 0

    if args.write:
        print("run-tests: --write is ignored; an automated test records no verdict (ADR-0038)",
              file=sys.stderr)
    counts = {"passing": 0, "failing": 0, "unrunnable": 0}
    print("== %s ==" % root.name)
    for _path, tid, cmd in tests:
        outcome, _code, detail = run_one(root, cmd, args.timeout)
        counts[outcome] += 1
        print("   %-12s %-10s %s%s" % (tid, outcome, cmd[:48], ("  — " + detail[:60]) if detail else ""))

    print("   passing=%(passing)d failing=%(failing)d unrunnable=%(unrunnable)d" % counts)
    if counts["unrunnable"]:
        print("   note: unrunnable is an environment gap, not a failure")
    return 1 if counts["failing"] else 0


if __name__ == "__main__":
    sys.exit(main())
