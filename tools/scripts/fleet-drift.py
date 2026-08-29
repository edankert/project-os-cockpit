#!/usr/bin/env python3
"""Report how far each repo's validator has fallen behind upstream (TASK-0585).

`PHASE-041` exists because the fleet drifted from upstream for months while
every routine sync reported success: `sync-project-os.sh` classifies a stale
`validate-docs.py` as DIVERGED and skips it, so nothing said the number was
growing. Measured 2026-08-18 and again 2026-08-29, the divergence grew ~93 lines
in eleven days, uniformly, while nobody did anything wrong. A one-shot catch-up
regresses on that schedule, so the number is measured continuously instead.

**What is measured is which RULES a repo runs, not how many lines it differs
by.** Line divergence answers the wrong question: `project-os-cockpit` is 1105
lines from upstream and is *ahead* of it -- new rules are authored there and
upstreamed -- while a repo can be 600 lines behind and still, in principle, run
every rule. The rule codes a validator emits are the thing a fleet either shares
or does not, and they separate the two cases cleanly: measured after PHASE-041,
the four migrated repos and the cockpit are missing **0** of upstream's 52
codes, and the six repos that hold no acceptance checks are each missing **10**.

Line divergence is still reported, because it is the number ISS-0209 tracked and
a reader comparing to that history needs it.

Exit codes:
    0   every gated repo runs every upstream rule
    1   a gated repo is behind
    2   the comparison could not be made (no upstream, or a gated repo has no
        validator) -- deliberately NOT 0, because "could not look" reporting
        success is the failure this whole phase is about

Usage:
    fleet-drift.py [FLEET_ROOT] [--upstream PATH] [--threshold N]
                   [--gate-all] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALIDATOR_REL = "tools/scripts/validate-docs.py"

#: Every way the validator names a gate when it reports one. Kept as one regex
#: rather than a hand-maintained list of codes, so a rule added upstream is
#: measured the day it lands rather than the day somebody remembers this file.
RULE_RE = re.compile(
    r'(?:report\.(?:error|warn)|emit|emit_for|promotion_emit)\('
    r'\s*(?:report,\s*)?"([A-Z][A-Z0-9-]*)"')

#: How a repo is judged to hold acceptance checks: notes at `level: acceptance`.
#: Counted from the text rather than parsed, because this script must run against
#: a repo whose validator it cannot import.
ACCEPTANCE_RE = re.compile(r"^level:\s*acceptance\s*$", re.MULTILINE)

ABSENT = "absent"
OK = "ok"
BEHIND = "behind"


def rule_codes(path: Path):
    return set(RULE_RE.findall(path.read_text(encoding="utf-8", errors="replace")))


def line_divergence(a: Path, b: Path) -> int:
    """Non-blank, whitespace-normalised lines of `a` absent from `b`.

    ISS-0209's number, kept for continuity with the history it recorded.
    """
    bl = {l.strip() for l in b.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()}
    return sum(1 for l in a.read_text(encoding="utf-8", errors="replace").splitlines()
               if l.strip() and l.strip() not in bl)


def count_acceptance_checks(repo: Path) -> int:
    docs = repo / "docs"
    if not docs.is_dir():
        return 0
    n = 0
    for md in docs.rglob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # The frontmatter block, however long it is. An earlier cut read a fixed
        # 2000-character head, which happened to be enough for every note in the
        # fleet today -- a counter that is right by luck under-reports the day
        # somebody writes a longer preamble, and under-reporting checks here
        # silently un-gates a repo.
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if ACCEPTANCE_RE.search(text[:end] if end != -1 else text):
            n += 1
    return n


def survey(fleet_root: Path, upstream: Path):
    up_validator = upstream / VALIDATOR_REL
    if not up_validator.is_file():
        raise FileNotFoundError(str(up_validator))
    up_codes = rule_codes(up_validator)
    rows = []
    for snap in sorted(fleet_root.glob("*/SNAPSHOT.yaml")):
        repo = snap.parent
        validator = repo / VALIDATOR_REL
        row = {"repo": repo.name, "checks": count_acceptance_checks(repo)}
        if not validator.is_file():
            # Reported as its own state. A repo with no validator is NOT a
            # repo with zero divergence, and collapsing the two is how a fleet
            # check reports health it never measured.
            row.update(status=ABSENT, missing_rules=[], missing_lines=None, gate=None)
            rows.append(row)
            continue
        text = validator.read_text(encoding="utf-8", errors="replace")
        missing = sorted(up_codes - rule_codes(validator))
        row.update(status=BEHIND if missing else OK,
                   missing_rules=missing,
                   missing_lines=line_divergence(up_validator, validator),
                   gate=text.count("_acceptance_is_settled"))
        rows.append(row)
    return up_codes, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parents[2]
    ap.add_argument("fleet_root", nargs="?", default=str(here.parent))
    ap.add_argument("--upstream", default=str(here.parent / "project-os"))
    ap.add_argument("--threshold", type=int, default=0,
                    help="Upstream rule codes a gated repo may be missing (default 0). "
                         "0 because after PHASE-041 every gated repo is at 0, and a "
                         "threshold set above the measured value is a guard that has "
                         "never been true.")
    ap.add_argument("--gate-all", action="store_true",
                    help="Fail for every repo, not only those holding acceptance checks.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    fleet_root = Path(args.fleet_root).expanduser().resolve()
    upstream = Path(args.upstream).expanduser().resolve()
    try:
        up_codes, rows = survey(fleet_root, upstream)
    except FileNotFoundError as exc:
        print("fleet-drift: no upstream validator at %s -- cannot compare, which is "
              "not the same as no drift" % exc, file=sys.stderr)
        return 2

    for row in rows:
        row["gated"] = bool(args.gate_all or row["checks"])

    if args.json:
        print(json.dumps({"upstream": str(upstream), "rules": len(up_codes), "repos": rows},
                         indent=2, sort_keys=True))
    else:
        print("fleet-drift: %d upstream rule codes, %d repo(s) under %s"
              % (len(up_codes), len(rows), fleet_root))
        print("%-28s %-7s %6s %8s %7s %8s" % ("repo", "state", "gate", "missing", "checks", "lines"))
        for row in rows:
            mark = "*" if row["gated"] else " "
            print("%-28s %-7s %6s %8s %7s %8s%s"
                  % (row["repo"], row["status"],
                     "-" if row["gate"] is None else row["gate"],
                     len(row["missing_rules"]) if row["status"] != ABSENT else "-",
                     row["checks"],
                     "-" if row["missing_lines"] is None else row["missing_lines"],
                     mark))
        print("  (* gated: holds acceptance checks)" if not args.gate_all else "  (* all gated)")

    failures, unmeasurable = [], []
    for row in rows:
        if not row["gated"]:
            continue
        if row["status"] == ABSENT:
            unmeasurable.append(row)
        elif len(row["missing_rules"]) > args.threshold:
            failures.append(row)

    for row in unmeasurable:
        print("fleet-drift: %s holds %d acceptance check(s) and has no %s -- the gate "
              "cannot run where the checks are" % (row["repo"], row["checks"], VALIDATOR_REL),
              file=sys.stderr)
    for row in failures:
        print("fleet-drift: %s is missing %d upstream rule(s): %s"
              % (row["repo"], len(row["missing_rules"]), ", ".join(row["missing_rules"])),
              file=sys.stderr)

    ungated_behind = [r for r in rows if not r["gated"] and r["status"] == BEHIND]
    if ungated_behind:
        # Reported loudly and not failed. ADR-0011 clause 3: a check promoted
        # over existing debt fails every build on the day it ships and gets
        # switched off. These repos hold no acceptance checks, so the gate has
        # nothing to gate there -- but silence would let them keep drifting,
        # which is the thing this file exists to stop.
        # stderr, never stdout: under --json stdout is a document, and a
        # trailing human line makes it unparseable. Found by piping this
        # script's own --json into `json.load`.
        print("fleet-drift: NOT GATED but behind -- %s"
              % ", ".join("%s (%d rules, %d lines)"
                          % (r["repo"], len(r["missing_rules"]), r["missing_lines"])
                          for r in ungated_behind),
              file=sys.stderr if args.json else sys.stdout)

    if unmeasurable:
        return 2
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
