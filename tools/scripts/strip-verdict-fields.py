#!/usr/bin/env python3
"""Remove the seven verdict fields from acceptance notes ([[TASK-0531]]).

The note holds intent; the ledger holds reality ([[ADR-0037]]). This is the
second half of that move, and it is the destructive half — so it refuses
before it writes rather than reporting after.

**The safety property, and it is the whole script:** no verdict may be removed
that the ledger does not already carry. `mark: done` on a note with no ledger
entry is a walked check about to become an unwalked one, silently, with the
evidence deleted in the same commit. The check is per note and the refusal
names every one it would have lost.

Usage:
    strip-verdict-fields.py --repo-root . --platform macos [--apply]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from project_os_cockpit import acceptance as A          # noqa: E402
from project_os_cockpit import ledger as L              # noqa: E402
from project_os_cockpit.index import Index              # noqa: E402

FIELDS = ("mark", "verdict_date", "verdict_reason", "invalidated_by",
          "automation", "covered_by", "evidence",
          #: ISS-0224 — a position in a document that no longer exists. No
          #: verdict rides on these, so the safety check does not apply to
          #: them; they are removed with the rest because they are the same
          #: kind of thing, a field the note no longer needs to carry.
          "section", "ordinal")
#: A scalar mark that says nothing was ever recorded. Removing one of these
#: loses no verdict, so a check at `todo` needs no ledger entry to be safe.
EMPTY_MARKS = {"todo", "", " ", "rerun"}

_FIELD_RE = re.compile(r"^(%s):" % "|".join(FIELDS))


def strip(text: str) -> tuple[str, list[str]]:
    """The note without its verdict fields, and which ones went.

    Line-oriented, like every other frontmatter write in this project
    (`note_writes._set_field`): a YAML round-trip would reformat every note it
    touched and bury the one real change in a whitespace diff.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text, []
    try:
        end = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
    except StopIteration:                                # pragma: no cover
        return text, []
    out, removed, skipping = [], [], False
    for i, line in enumerate(lines):
        if 0 < i < end:
            found = _FIELD_RE.match(line)
            if found:
                removed.append(found.group(1))
                #: A block field (`invalidated_by:` with nested keys) takes its
                #: continuation lines with it. Dropping the key and leaving the
                #: body would make the note unparseable — a defect that reads
                #: as a missing note rather than as a bad edit.
                skipping = True
                continue
            if skipping:
                if line[:1].isspace() and line.strip():
                    continue
                skipping = False
        out.append(line)
    return "\n".join(out) + "\n", removed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--platform", required=True,
                    help="the platform whose ledger must already carry these "
                         "verdicts")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    docs = root / "docs"
    if not L.has_ledger(docs):
        print("strip: this repo has no ledger — removing the fields would "
              "delete every verdict it has. Run backfill-ledger.py first.")
        return 2

    #: Indexed, for the reason `backfill-ledger.py` learned the hard way: the
    #: un-indexed read walks `docs/tests/acceptance/` only, and a check filed
    #: anywhere else would be stripped without ever having been backfilled.
    suite = A.load(docs, Index.build(docs))
    carried = L.verdicts(docs, args.platform)

    return _run(root, docs, suite, carried, args)


def _frontmatter_mark(text: str) -> str:
    """The `mark:` **as the file stores it**.

    `Item.mark` is not that. `acceptance.load` applies the ledger to every
    item, so an `Item`'s mark is the ledger's answer — and a guard that
    compared it to the ledger was comparing the ledger to itself. Reproduced
    by independent review 2026-08-19: three notes at `mark: done`, a ledger
    with **zero** entries, and this script printed *"every non-empty mark is
    carried"* while deleting all three.

    The safety property is about what is on disk, so it is read from disk.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("mark:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""

def _run(root, docs, suite, carried, args) -> int:
    would_lose, targets = [], []
    for item in suite.items:
        if not item.rel:
            continue
        path = docs / item.rel
        text = path.read_text(encoding="utf-8")
        _, removed = strip(text)
        if not removed:
            continue
        #: **From the file, never from the Item.** See `_frontmatter_mark`.
        mark = _frontmatter_mark(text)
        if mark not in EMPTY_MARKS and item.note_id not in carried:
            would_lose.append(f"{item.note_id}: `mark: {mark}` and no entry "
                              f"in the {args.platform} ledger ({item.rel})")
        targets.append((path, text, removed))

    if would_lose:
        print(f"strip: REFUSING — {len(would_lose)} note(s) carry a verdict "
              f"the ledger does not, and stripping would delete it:")
        for line in would_lose[:40]:
            print(f"  - {line}")
        if len(would_lose) > 40:
            print(f"  … and {len(would_lose) - 40} more")
        return 1

    print(f"strip: {root.name} / {args.platform}")
    print(f"  acceptance notes   {len(suite.items)}")
    print(f"  notes to strip     {len(targets)}")
    print(f"  ledger entries     {len(carried)} — every non-empty mark is "
          f"carried")
    if not args.apply:
        print("strip: dry run — nothing written. Re-run with --apply.")
        return 0
    for path, text, _removed in targets:
        path.write_text(strip(text)[0], encoding="utf-8")
    print(f"strip: rewrote {len(targets)} note(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
