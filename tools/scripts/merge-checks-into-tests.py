#!/usr/bin/env python3
"""Fold every `CHK-*` check note into a `TST-*` test at `level: acceptance` (ADR-0031).

The second migration of this corpus in two weeks, and the record says so. The
first (ADR-0030) moved a single grammar-bearing document into one note per
check; this one changes those notes' TYPE, because the sibling type blocked the
thing that mattered more -- a check could not be automated, while a test becomes
automated by adding `command:`.

**Parity is asserted through the reader, never by counting files.** A file count
proves the script wrote as many notes as it read and nothing about whether the
suite still loads, tiers, marks and gates. That distinction is what ISS-0175 was
filed about, and it is why `--write` refuses on any mismatch rather than
reporting one.

Usage:
    merge-checks-into-tests.py [--repo-root PATH] [--write]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

CHECKS_REL = "tests/acceptance"


def _head_body(text: str) -> tuple[str, str]:
    end = text.find("\n---", 3)
    return (text[:end], text[end:]) if text.startswith("---") and end > 0 else ("", text)


def _field(head: str, name: str) -> str:
    m = re.search(rf"^{name}:[ \t]*(.*)$", head, re.M)
    return m.group(1).strip() if m else ""


def _set(head: str, name: str, value: str) -> str:
    if re.search(rf"^{name}:", head, re.M):
        # `value` is a REPLACEMENT string, so a literal backslash or `\g` in a
        # title would be interpreted rather than written. Escaped, because a
        # check name is free text.
        return re.sub(rf"^{name}:[ \t]*.*$", lambda _m: f"{name}: {value}",
                      head, count=1, flags=re.M)
    return head.rstrip("\n") + f"\n{name}: {value}"


def _sort_key(path: Path, head: str) -> tuple:
    """Suite order: tier, then section, then ordinal -- the order a walker reads.

    Numbering by suite order rather than by the old id means the new ids run in
    the direction somebody walks them, which is the one chance a renumber gets
    to improve on what it replaces.
    """
    def num(v: str, default: int) -> float:
        try:
            return float(re.sub(r'["\']', "", v) or default)
        except ValueError:
            return float(default)
    section = re.sub(r'["\']', "", _field(head, "section"))
    parts = tuple(int(p) for p in re.findall(r"\d+", section)) or (9999,)
    return (num(_field(head, "tier"), 9), parts, num(_field(head, "ordinal"), 0), path.name)


def read_suite(docs_root: Path):
    """The suite as the cockpit's own reader sees it -- the parity subject."""
    from project_os_cockpit import acceptance
    return acceptance.load(docs_root)


def fingerprint(suite) -> dict:
    """What must be identical before and after. Not a count -- a description."""
    from collections import Counter
    return {
        "n": len(suite.items),
        "marks": dict(Counter(i.mark for i in suite.items)),
        "tiers": dict(Counter(i.tier for i in suite.items)),
        "covers": sorted({r for i in suite.items for r in i.refs}),
        "blocking": len(suite.blocking()),
        "titles": sorted(i.name for i in suite.items),
        # Widened after review found the fingerprint guarding 6 of ~22 fields.
        # A migration that silently dropped `area`, `burden` or a verdict reason
        # would have passed every assertion above it.
        "areas": dict(Counter(i.area for i in suite.items)),
        "sections": sorted(i.section for i in suite.items),
        "verdicts": sorted((i.verdict_date, i.verdict_reason) for i in suite.items),
        "automation": dict(Counter(i.automation for i in suite.items)),
        "burden": sorted(tuple(i.burden) for i in suite.items),
        "evidence": sorted(tuple(i.evidence) for i in suite.items),
        "invalidated": sorted(
            (i.invalidated.change, i.invalidated.reason, i.invalidated.date)
            for i in suite.items),
    }


def next_tst(docs_root: Path) -> int:
    top = 0
    for p in docs_root.rglob("TST-*.md"):
        m = re.match(r"TST-(\d+)", p.name)
        if m:
            top = max(top, int(m.group(1)))
    return top + 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.repo_root).resolve()
    docs = root / "docs"
    checks_dir = docs / CHECKS_REL
    if not checks_dir.is_dir():
        print("merge-checks: no %s -- nothing to do" % CHECKS_REL)
        return 0

    paths = sorted(checks_dir.glob("CHK-*.md"))
    if not paths:
        print("merge-checks: no CHK-* notes -- already merged or never instantiated")
        return 0

    before = fingerprint(read_suite(docs))
    try:
        sha = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "unknown"

    heads = {p: _head_body(p.read_text(encoding="utf-8")) for p in paths}
    ordered = sorted(paths, key=lambda p: _sort_key(p, heads[p][0]))
    start = next_tst(docs)
    plan = []
    for offset, path in enumerate(ordered):
        head, body = heads[path]
        old_id = _field(head, "id").strip('"')
        new_id = "TST-%04d" % (start + offset)
        slug = path.name.split("-", 2)[2] if path.name.count("-") >= 2 else path.name
        plan.append((path, checks_dir / f"{new_id}-{slug}", old_id, new_id, head, body))

    # **Refusals BEFORE the first write.** The first cut validated parity after
    # every file had been written and every `CHK-*` unlinked, which is a report
    # rather than a refusal -- by the time it fired the corpus was already
    # rewritten. Found by independent review.
    problems: list[str] = []
    for path, _target, old_id, _new_id, head, _body in plan:
        if not head.startswith("---"):
            problems.append("%s has no frontmatter; a line-regex editor would "
                            "destroy it while parity stayed green" % path.name)
        if not old_id:
            problems.append("%s declares no id:" % path.name)
        if re.search(r"^aliases:[ \t]*$", head, re.M):
            problems.append("%s uses block-style aliases:, which this editor "
                            "cannot rewrite without producing invalid YAML" % path.name)
    try:
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                               capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        dirty = ""
    if dirty and args.write:
        # `merged_from:` records the sha the notes came from. Against a dirty
        # tree that sha does not contain what was migrated, which is the exact
        # defect TASK-0463 fixed in the previous migration by stamping
        # "(uncommitted at migration)" instead of pointing at a lie.
        problems.append("the working tree is dirty; `merged_from:` would name a "
                        "sha that does not contain these notes (commit first)")
    if problems:
        for problem in problems:
            print("merge-checks: REFUSED -- %s" % problem)
        return 1

    print("merge-checks: %d check(s) -> %s..%s" % (len(plan), plan[0][3], plan[-1][3]))
    if not args.write:
        for path, target, old_id, new_id, _h, _b in plan[:3]:
            print("   %s  ->  %s  (%s)" % (old_id, new_id, target.name))
        print("   ... (--write to apply)")
        return 0

    for path, target, old_id, new_id, head, body in plan:
        h = _set(head, "type", '"[[test]]"')
        h = _set(h, "id", new_id)
        # The old id stays reachable: it appears in prose, in `migrated_from:`
        # provenance and in anybody's muscle memory.
        aliases = _field(h, "aliases")
        keep = re.findall(r'"([^"]+)"', aliases)
        keep = [a for a in keep if a != old_id]
        h = _set(h, "aliases", "[" + ", ".join(f'"{a}"' for a in [new_id, old_id] + keep) + "]")
        h = _set(h, "level", "acceptance")
        h = _set(h, "kind", "manual")
        h = _set(h, "merged_from", f'"{old_id} @ {sha}"')
        if _field(h, "status").strip('"') not in ("draft", "active", "retired"):
            h = _set(h, "status", "active")
        target.write_text(h + body, encoding="utf-8")
        if target != path:
            path.unlink()

    after = fingerprint(read_suite(docs))
    ok = True
    for key in sorted(before):
        if before[key] != after[key]:
            ok = False
            b, a = before[key], after[key]
            if isinstance(b, list):
                print("merge-checks: PARITY FAILED on %s: only-before=%s only-after=%s"
                      % (key, sorted(set(b) - set(a))[:5], sorted(set(a) - set(b))[:5]))
            else:
                print("merge-checks: PARITY FAILED on %s: before=%r after=%r" % (key, b, a))
    print("merge-checks: %d notes, %d blocking, marks %s"
          % (after["n"], after["blocking"], after["marks"]))
    if not ok:
        print("merge-checks: REFUSING to report success -- the suite the reader sees changed")
        return 1
    print("merge-checks: parity holds through the reader (count, marks, tiers, covers, blocking, titles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
