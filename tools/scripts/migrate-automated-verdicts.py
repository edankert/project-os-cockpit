#!/usr/bin/env python3
"""Strip the verdict from every test note a machine executes (ADR-0038).

A note carrying a `command:` records **that a machine executes it**. It must not
record whether it passed. This removes the four fields that said otherwise:

    status: passing|failing|ready   ->  active   (retired is left alone)
    last_run:                       ->  removed
    exit_code:                      ->  removed

Measured across the fleet on 2026-08-19, before this ran: 139 automated notes
carried **49 verdicts, 50 `last_run` and 108 `exit_code`**. `your-trainer` alone
held 69 exit codes against 2 verdicts -- the residue of a runner writing a value
the validator forbids on `level: acceptance`, where 89 of its 91 automated notes
sit. The most-written field on the automated corpus was the one that meant least.

**Run `run-tests.py`'s de-fanging first** (TASK-0559). Cleaning the corpus while
the runner still stamps means the next execution re-stamps what was just
stripped.

Reports before/after counts per repo, because [[TASK-0562]] is discharged by the
numbers rather than by the script exiting 0. Dry run by default.

Stdlib only. Usage:
    migrate-automated-verdicts.py [--repo-root PATH] [--apply]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: Statuses an automated note must not hold. `ready` is the obligation
#: registry's `Run` -- an automated test is never owed to a person -- and
#: `passing`/`failing` are the verdict itself. Identical to the set
#: `ACCEPTANCE_FORBIDDEN_STATUSES` has always applied at `level: acceptance`;
#: ADR-0038 is that set's domain widening, not a new rule.
FORBIDDEN_STATUSES = ("ready", "passing", "failing")

#: Evidence of an execution. Meaningless once the verdict is gone, and actively
#: misleading while it lingers: a note reading `exit_code: 1` beside a status
#: nobody wrote claims a failure that no longer exists anywhere.
EVIDENCE_FIELDS = ("last_run", "exit_code")


def split_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[:4], text[4:end], text[end:]


def fm_get(fm, key):
    m = re.search(r"^%s:\s*(.*)$" % re.escape(key), fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def strip(fm):
    """Return (new_fm, what_changed). Pure -- the caller decides to write."""
    changed = []
    status = fm_get(fm, "status").lower()
    if status in FORBIDDEN_STATUSES:
        fm = re.sub(r"^status:.*$", "status: active", fm, count=1, flags=re.M)
        changed.append("status:%s->active" % status)
    for key in EVIDENCE_FIELDS:
        if re.search(r"^%s:" % re.escape(key), fm, re.M):
            # Drop the whole line. Blanking it would leave `exit_code: ""`,
            # which is the field still being there and saying nothing.
            fm = re.sub(r"^%s:.*\n?" % re.escape(key), "", fm, count=1, flags=re.M)
            changed.append("-" + key)
    return fm, changed


def census(root):
    """(automated, verdicts, last_run, exit_code) over every TST-* note."""
    n = v = lr = ec = 0
    for path, fm in walk(root):
        n += 1
        if fm_get(fm, "status").lower() in FORBIDDEN_STATUSES:
            v += 1
        lr += bool(re.search(r"^last_run:", fm, re.M))
        ec += bool(re.search(r"^exit_code:", fm, re.M))
    return n, v, lr, ec


def walk(root):
    docs = root / "docs"
    if not docs.is_dir():
        return
    for path in sorted(docs.rglob("TST-*.md")):
        if "__templates__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        parts = split_frontmatter(text)
        if not parts:
            continue
        _pre, fm, _post = parts
        if not fm_get(fm, "command"):
            continue
        yield path, fm


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true", help="Write (default: report only)")
    args = ap.parse_args(argv)

    root = Path(args.repo_root).resolve()
    if not (root / "SNAPSHOT.yaml").is_file():
        print("migrate: no SNAPSHOT.yaml at %s" % root, file=sys.stderr)
        return 2

    before = census(root)
    print("== %s ==" % root.name)
    print("   before: automated=%d verdicts=%d last_run=%d exit_code=%d" % before)

    touched = 0
    for path, _fm in list(walk(root)):
        text = path.read_text(encoding="utf-8")
        pre, fm, post = split_frontmatter(text)
        new_fm, changed = strip(fm)
        if not changed:
            continue
        touched += 1
        print("   %-46s %s" % (path.name[:46], " ".join(changed)))
        if args.apply:
            path.write_text(pre + new_fm + post, encoding="utf-8")

    if args.apply:
        after = census(root)
        print("   after:  automated=%d verdicts=%d last_run=%d exit_code=%d" % after)
        if after[1:] != (0, 0, 0):
            print("   FAILED: fields remain", file=sys.stderr)
            return 1
    print("   %d note(s) %s" % (touched, "changed" if args.apply else "would change"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
