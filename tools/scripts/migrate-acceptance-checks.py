#!/usr/bin/env python3
"""Turn `docs/tests/ACCEPTANCE_TESTS.md` into one `CHK-*` note per check.

[[ADR-0030]] / [[TASK-0460]]. `acceptance.parse` already yields every field the
document holds — tier, section, area, ordinal, mark, refs, the `RE-RUN`
annotation, the prose — so the script is: parse, write N notes, prove nothing
was lost, delete the source, write a README that says where the history went.

**Parity is asserted, never assumed.** [[ISS-0175]] is the record of what
assuming costs: a mapping that "obviously" held drifted by 37 rows on the one
corpus it ran against, and 285 of 542 rendered rows carried another row's text
for eleven days. So this reloads what it wrote, through the real reader, and
compares every row field by field. **The source file is deleted only after
parity is green** — a migration that loses rows and then removes the evidence
is the one failure mode with no recovery short of git.

Deliberately reads exactly one path, so the frozen per-release snapshot suites
(`ACCEPTANCE_TESTS_v2.1.0.md`, `ACCEPTANCE_CHECKLIST_v2.1.1.md`) are untouched
by construction rather than by an exclusion somebody has to maintain. Those are
records of what past releases were measured against; rewriting them would
falsify history.

Usage:
    migrate-acceptance-checks.py --repo-root <path> [--apply]

Without `--apply` it writes nothing and prints what it would do, including the
parity result — a dry run that cannot tell you whether the migration is safe is
not worth having.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from project_os_cockpit import acceptance as A  # noqa: E402

#: The mark a migrated note is written with. ADR-0029: the legacy characters
#: stay READABLE forever and are never WRITTEN — and a migration writes every
#: note in the corpus, so it is the one place the distinction has teeth.
#: Normalising `~` -> `/` is not a verdict change: both are *incomplete*, and
#: parity below compares the CLASSIFICATION, which is what a gate reads.
NORMALISE = dict(A.LEGACY_MARKS)

STOPWORDS = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "is", "it"}


def slug(name: str, *, words: int = 6) -> str:
    """`Serve a repo` -> `Serve-A-Repo`. Short, stable, and never empty."""
    cleaned = re.sub(r"[^A-Za-z0-9 ]+", " ", name or "")
    parts = [w for w in cleaned.split() if w]
    kept = [w for w in parts if w.lower() not in STOPWORDS] or parts
    out = "-".join(w[:1].upper() + w[1:] for w in kept[:words])
    return out or "Check"


def _git(root: Path, *args: str) -> str:
    try:
        done = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                              text=True, timeout=20, check=False)
    except (OSError, subprocess.SubprocessError):     # pragma: no cover
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def strip_annotation(text: str) -> str:
    """The check's prose with the `RE-RUN (…)` annotation lifted out of it.

    The annotation stops being prose and becomes `invalidated_by:` — that is
    TESTING.md rule 3 turning from something people write in a sentence into
    something a surface can act on. Only its POSITION in the line is not
    preserved, and it does not need to be: 26 of the fleet's 54 put it
    mid-sentence, so preserving position would mean preserving 54 different
    sentence shapes to no reader's benefit.
    """
    out = text or ""
    while True:
        found = A._RERUN_RE.search(out)
        if found is None:
            return out.strip()
        left, right = out[:found.start()], out[found.end():]
        # Repair ONLY the seam. The first version collapsed every run of
        # whitespace in the line, which silently rewrote prose two hundred
        # characters away — a row reading `OWED  [Accept] [Supersede]`, where
        # the double space is the rendered gap between a label and its
        # buttons. Parity caught it, which is the argument for asserting the
        # prose rather than trusting a regex to be conservative.
        left = re.sub(r"[\s]*[—–-]?[\s]*$", "", left)
        right = right.lstrip()
        if not left:
            out = re.sub(r"^[—–-]\s*", "", right)
        elif not right:
            out = left
        elif right[0] in ".,;:)":
            out = left + right
        else:
            out = left + " " + right


def note_text(item: A.Item, *, check_id: str, sha: str, ordinal: int,
              uncommitted: bool = False) -> str:
    """One `CHK-*` note, in the template's shape."""
    fm: list[str] = [
        "---",
        'type: "[[check]]"',
        f"id: {check_id}",
        f'aliases: ["{check_id}"]',
        f"title: {_yaml(item.name)}",
        # `active`, always. Whether a check describes a surface that has been
        # retired is a JUDGEMENT, and a migration that made 669 of them at once
        # would be inventing state rather than moving it. The one row in this
        # repo whose prose says its surface was retired keeps its `/` mark and
        # its reasoning, and a person can retire it in one edit.
        "status: active",
        "owner: user:edwin",
        f"created: {_today()}",
        f"updated: {_today()}",
        f"tier: {item.tier}",
        f"area: {_yaml(item.area)}",
        f"section: {_yaml(item.section)}",
        # Sparse by ten, which is what retires the shifting address: a check
        # inserted between two others takes a number between theirs and moves
        # nothing. The old scheme renumbered every row below an insert, and
        # `locate()` exists because of it.
        f"ordinal: {ordinal}",
        f"mark: {_yaml(NORMALISE.get(item.mark, item.mark))}",
        f"verdict_date: {_yaml(item.verdict_date)}",
        f"verdict_reason: {_yaml(item.verdict_reason)}",
    ]
    if item.invalidated:
        fm.append("invalidated_by:")
        fm.append(f"  change: {_yaml(item.invalidated.change)}")
        fm.append(f"  reason: {_yaml(item.invalidated.reason)}")
        fm.append(f'  date: ""')
        fm.append(f"  raw: {_yaml(item.invalidated.raw)}")
    else:
        fm.append("invalidated_by: {}")
    # Never inferred from prose. TASK-0449 tried exactly that and measured a
    # 6-of-6 false-positive rate on the only corpus it would have run against;
    # `manual` is what every migrated row honestly is until somebody says
    # otherwise, and a wrong `full` would claim coverage that does not exist.
    fm.extend([
        "automation: manual",
        "covered_by: []",
        f"covers: [{', '.join(f'\"[[{r}]]\"' for r in item.refs)}]",
        "burden: []",
        "evidence: []",
        # **The sha must contain the row it stamps.** A suite with uncommitted
        # rows migrates them like any other, and stamping them with HEAD would
        # point at a commit that does not hold them — wrong in precisely the
        # field that exists because blame cannot cross the migration commit.
        # Measured on `../your-trainer`: 560 rows at HEAD, 579 in the working
        # tree. Nineteen notes would have carried a false provenance, and the
        # nineteen NEWEST ones at that.
        f"migrated_from: {_yaml(f'{A.SUITE_REL}#{item.number} @ {sha}' + (' (uncommitted at migration)' if uncommitted else ''))}",
        "related: []",
        "---",
        "",
        f"# {item.name}",
        "",
        # The annotation is NOT prose any more: it left the sentence and became
        # `invalidated_by:` above. Writing `item.text` here was the first cut
        # and left both copies in place — caught by parity on `your-trainer`'s
        # 54 annotated rows, which is exactly the population it exists for.
        strip_annotation(item.text),
        "",
    ])
    return "\n".join(fm)


def _today() -> str:
    import datetime
    return datetime.date.today().isoformat()


def _yaml(value: str) -> str:
    """A frontmatter scalar that survives the round trip.

    Everything is quoted and escaped rather than emitted bare: the corpus's
    check names contain colons (`**Serve a repo:**`), `#`, quotes and em-dashes,
    and a bare scalar carrying any of them either fails to parse or silently
    truncates at the comment marker.
    """
    text = str(value or "")
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ----------------------------------------------------------------- parity

FIELDS = ("tier", "section", "area", "name", "checked", "reconciled",
          "excepted", "failed", "question", "settled", "stale")


def compare(before: list[A.Item], after: list[A.Item]) -> list[str]:
    """Every way the migration could have lost something, checked.

    Ordered pairwise rather than matched by name: two checks in one suite may
    legally share a name (`your-trainer` has several), and a name-keyed compare
    would silently pass while two rows swapped verdicts.
    """
    problems: list[str] = []
    if len(before) != len(after):
        problems.append(f"row count: {len(before)} in, {len(after)} out")
        return problems
    for old, new in zip(before, after):
        for field in FIELDS:
            if getattr(old, field) != getattr(new, field):
                problems.append(
                    f"{old.number} {old.name!r}: {field} "
                    f"{getattr(old, field)!r} -> {getattr(new, field)!r}")
        if tuple(old.refs) != tuple(new.refs):
            problems.append(f"{old.number} {old.name!r}: refs "
                            f"{old.refs} -> {new.refs}")
        if old.invalidated.raw != new.invalidated.raw:
            problems.append(f"{old.number} {old.name!r}: RE-RUN annotation "
                            f"{old.invalidated.raw!r} -> {new.invalidated.raw!r}")
        if strip_annotation(old.text) != new.text:
            problems.append(f"{old.number} {old.name!r}: prose changed")
    # The two numbers a release is decided by, asserted in their own right
    # rather than inferred from the rows above — a gate that agrees row by row
    # and disagrees in total is the kind of thing this project has shipped.
    for label, fn in (("settled", lambda s: sum(1 for i in s if i.settled)),
                      ("blocking", lambda s: sum(
                          1 for i in s
                          if i.tier in A.GATING_TIERS and not i.settled))):
        if fn(before) != fn(after):
            problems.append(f"{label}: {fn(before)} -> {fn(after)}")
    return problems


# ----------------------------------------------------------------- the README

README_HEAD = """---
type: "[[reference]]"
id: ACCEPTANCE-TESTS
aliases: ["ACCEPTANCE-TESTS", "ACCEPTANCE_TESTS"]
title: "Acceptance checks — where they live and how to read their history"
status: active
owner: user:edwin
created: {created}
updated: {updated}
scope: tests
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# Acceptance checks

**One note per check**, in this directory, named `CHK-####-Slug.md`. `status:`
is the lifecycle (`draft`/`active`/`retired`) and **`mark:` is the verdict** —
ticking a check never touches its status. The suite is read as a list by the
cockpit's acceptance view; there is no document to open, because the document
*was* the display and that is the thing [[ADR-0030]] changed.

## Reading history from before the migration

Until `{sha}` this whole suite was one file, `docs/{suite_rel}`, and every
check was a line in it. That file was **deleted** rather than kept as a
tombstone: two copies of one record is the dual-source trap this project has
paid for twice, and git holds the file intact at every ref before the cut.

- The suite as it stood at any earlier ref: `git show <ref>:docs/{suite_rel}`
- One check's full line-by-line history: `git log -L '/<the check name>/',+1:docs/{suite_rel}`
- Each note carries `migrated_from:` — its old `#section.ordinal` address and
  the sha above — because blame does not cross the migration commit (~2%
  similarity; rename detection will not fire). Traceability is preserved by the
  record, deliberately, rather than by git plumbing that cannot carry it.

## What the file said, kept verbatim

Everything below is the migrated document's own prose, unchanged. The tier
sections became the notes; this is everything else it held.

"""


def build_readme(source_text: str, sha: str, created: str) -> str:
    """The README: pointer first, then the old document's prose verbatim.

    The preamble is not decoration — it holds the tier definitions, the five
    rules, and this repo's own account of every walk it has performed. A
    migration that dropped it would lose more words than it moved.
    """
    body = A._split_frontmatter(source_text)
    kept: list[str] = []
    in_tier = False
    for line in body.splitlines():
        if A._TIER_HEADING_RE.match(line):
            in_tier = True
            continue
        if line.startswith("# ") and not A._TIER_HEADING_RE.match(line):
            in_tier = False
        if not in_tier:
            kept.append(line)
    prose = "\n".join(kept).strip()
    return README_HEAD.format(
        created=created, updated=_today(), sha=sha or "the migration commit",
        suite_rel=A.SUITE_REL,
    ) + prose + "\n"


# ----------------------------------------------------------------- the run

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true",
                    help="write the notes and delete the source file")
    ap.add_argument("--start-id", type=int, default=0,
                    help="first CHK number; default reads counters.CHK")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    docs = root / "docs"
    source = docs / A.SUITE_REL
    if not source.exists():
        print(f"migrate: no suite at {source} — nothing to migrate")
        return 2
    out_dir = docs / A.CHECKS_REL
    if out_dir.exists() and any(out_dir.glob("CHK-*.md")):
        print(f"migrate: {out_dir} already holds checks — refusing to run twice")
        return 2

    text = source.read_text(encoding="utf-8")
    before = A.parse(text)
    if not before:
        print("migrate: the suite parses to zero checks — refusing")
        return 2
    sha = _git(root, "rev-parse", "--short", "HEAD")
    # Rows the committed file does not have. Keyed on tier+name, the same key
    # the release-gate delta diffs on and for the same reason: a row's NUMBER
    # shifts when anything above it is inserted, so numbering would report
    # every row below an insert as new.
    at_head = _git(root, "show", f"HEAD:docs/{A.SUITE_REL}")
    committed = {(i.tier, i.name.strip().casefold()) for i in A.parse(at_head)} \
        if at_head else set()
    fresh = {(i.tier, i.name.strip().casefold()) for i in before} - committed \
        if committed else set()
    if fresh:
        print(f"migrate: {len(fresh)} row(s) are NOT in the committed file — "
              f"their notes record the sha with `(uncommitted at migration)`, "
              f"because {sha} does not contain them")

    start = args.start_id or _counter(root) + 1
    plan: list[tuple[str, Path, str]] = []
    per_section: dict[tuple[int, str], int] = {}
    for offset, item in enumerate(before):
        check_id = f"CHK-{start + offset:04d}"
        key = (item.tier, item.section)
        per_section[key] = per_section.get(key, 0) + 10
        path = out_dir / f"{check_id}-{slug(item.name)}.md"
        plan.append((check_id, path,
                     note_text(item, check_id=check_id, sha=sha,
                               ordinal=per_section[key],
                               uncommitted=(item.tier,
                                            item.name.strip().casefold())
                                           in fresh)))

    print(f"migrate: {len(plan)} checks from docs/{A.SUITE_REL} "
          f"-> docs/{A.CHECKS_REL}/  (ids {plan[0][0]}..{plan[-1][0]}, sha {sha})")

    # Written to a scratch directory first when this is a dry run, so parity is
    # measured on the real artefacts either way. A dry run that reports nothing
    # about correctness only tells you the script is willing to start.
    import shutil
    import tempfile
    target = out_dir if args.apply else Path(tempfile.mkdtemp()) / A.CHECKS_REL
    target.mkdir(parents=True, exist_ok=True)
    for _check_id, path, body in plan:
        (target / path.name).write_text(body, encoding="utf-8")

    after = A.load_notes(target)
    problems = compare(before, after)
    if problems:
        print(f"migrate: PARITY FAILED — {len(problems)} problem(s); nothing deleted")
        for line in problems[:40]:
            print(f"  - {line}")
        if not args.apply:
            shutil.rmtree(target.parent, ignore_errors=True)
        return 1

    settled = sum(1 for i in after if i.settled)
    blocking = sum(1 for i in after
                   if i.tier in A.GATING_TIERS and not i.settled)
    marks: dict[str, int] = {}
    for item in after:
        marks[item.mark] = marks.get(item.mark, 0) + 1
    print(f"migrate: parity OK — {len(after)} checks, {settled} settled, "
          f"{blocking} blocking, marks {marks}")

    if not args.apply:
        shutil.rmtree(target.parent, ignore_errors=True)
        print("migrate: dry run — nothing written. Re-run with --apply.")
        return 0

    created = _created_date(text) or _today()
    (out_dir / "README.md").write_text(
        build_readme(text, sha, created), encoding="utf-8")
    source.unlink()
    print(f"migrate: wrote {len(plan)} notes + README, deleted docs/{A.SUITE_REL}")
    print("migrate: raise counters.CHK with tools/scripts/sync-snapshot.py")
    return 0


def _counter(root: Path) -> int:
    """`counters.CHK` from SNAPSHOT.yaml, or 0. Read rather than assumed: an id
    handed out twice is the one migration error nothing downstream can undo."""
    try:
        text = (root / "SNAPSHOT.yaml").read_text(encoding="utf-8")
    except OSError:
        return 0
    found = re.search(r"^\s+CHK:\s*(\d+)\s*$", text, re.M)
    return int(found.group(1)) if found else 0


def _created_date(text: str) -> str:
    found = re.search(r"^created:\s*(\S+)\s*$", text, re.M)
    return found.group(1).strip('"') if found else ""


if __name__ == "__main__":
    raise SystemExit(main())
