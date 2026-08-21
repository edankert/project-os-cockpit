#!/usr/bin/env python3
"""A run emits what it observed covering ([[FEAT-0138]] / [[TASK-0543]]).

Reads the declarations (`coverage-declarations.py`) and the run's **JUnit XML**
— which pytest writes with `--junitxml` and gradle writes natively, so the two
toolchains [[TASK-0542]] names need no shared library here either — and appends
`method: automated` events to the working ledger for its platform.

## The three events, and why the middle one is not `mark: fail`

* **observed passing** → `mark: pass`, `by:` naming the test, `date:` the run.
* **observed failing** → an **invalidation**, not a `fail` verdict.
* **declared and not observed at all** → an **invalidation**.

`mark: fail` was the obvious choice and it is wrong. `fail` is a *walk* verdict
in the blocking vocabulary, so emitting it would put a machine-driven
population straight into the release gate — the behaviour change [[ADR-0031]]
recorded as a risk rather than discovering later. An invalidation says exactly
what is true: *the evidence for that verdict no longer holds*. The check goes
back on the run list without anybody asserting a walk that never happened.

**Emitting nothing on failure was rejected too**, and it was [[TASK-0543]]'s
other named option. It leaves the last green run's `pass` standing over a test
that now fails, which is the stale-verdict shape this whole phase exists to
remove.

The third event is [[TASK-0543]]'s fourth criterion and the whole point of the
inversion: **delete the covering test and its check reappears on the run list
by itself**, because the run stops observing it and says so.

## It appends only when the answer CHANGES

The ledger is an event log and an event is a change. Re-appending an identical
`pass` on every green run would grow the file without recording anything, and
`resolve()` would give the same answer either way. So the current resolved
verdict is read first and the entry is written only if it differs.

## It does not push

A commit is local and reversible; a push is publishing. This writes the
working ledger and stops. In GitHub Actions that means the entries live in the
workspace and are reported — landing them is a person's commit, like every
other write in this repo.

Usage:
    emit-coverage.py --repo-root R --junit report.xml --platform macos \\
                     --by "ci:validate-docs" [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def _scanner():
    """`coverage-declarations.py`, loaded by path.

    Its filename carries a hyphen — every script beside it does, and renaming
    one script to be importable would make the set inconsistent for the sake
    of one caller. `importlib` loads a path directly and costs a function.
    """
    import importlib.util

    here = Path(__file__).resolve().parent / "coverage-declarations.py"
    spec = importlib.util.spec_from_file_location("coverage_declarations", here)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def junit_results(path: Path) -> dict[str, bool]:
    """`{test name: passed}` from a JUnit XML report.

    **Keyed on the bare test name**, which is what the declaration scanner
    knows: pytest writes `name="test_x"` with the module in `classname`, and
    gradle writes the method name the same way. A skipped test is *not*
    observed — it is exactly the `@Ignore` case the inversion exists to catch,
    so it is absent from this map rather than present and true.
    """
    out: dict[str, bool] = {}
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        name = str(case.get("name") or "").strip()
        if not name:
            continue
        #: pytest parametrisation writes `test_x[param]`; the declaration
        #: names the function, so the parameter is stripped and every case
        #: must pass for the check to be observed passing.
        base = name.split("[", 1)[0]
        if any(case.find(tag) is not None for tag in ("skipped",)):
            continue
        ok = all(case.find(tag) is None for tag in ("failure", "error"))
        out[base] = out.get(base, True) and ok
    return out


def plan(root: Path, results: dict[str, bool], platform: str):
    """What this run should append: `(passing, failing, stale, current)`.

    A check is **observed passing** only when every test declaring it ran and
    passed. One declaring test failing is enough: a check covered by five tests
    is covered by all five, and reporting it as passing because four did is the
    overclaiming this phase spent itself removing.

    **`stale` is read from the LEDGER, not from the declarations**, and getting
    that backwards defeats the whole feature. The first cut computed *declared
    but not observed* — so deleting the test, which deletes the declaration
    too, removed the check from the set that could be invalidated and left it
    settled forever. That is `covered_by:`'s silent rot reproduced exactly, in
    the tool built to end it. Caught by
    `test_deleting_the_covering_test_puts_its_check_back_on_the_run_list`,
    which failed on the first run.

    So the question is asked of the standing verdict: *a machine claimed to
    cover this — did a machine cover it this time?*

    **`method: automated` and nothing else.** A person's `manual` walk and a
    `migration` backfill are not the emitter's to retract HERE: it observed
    nothing about this check in this run, so it can only take back a
    machine's claim. The `failing` branch is different and deliberately so —
    see :func:`main`.

    **It does NOT key on `by`.** The first cut did, and independent review
    reproduced the consequence: rename the CI job and every prior verdict is
    stranded permanently — the run stops recognising its own claims, the
    check stays settled with no covering test in the repo, and the output
    reads *"nothing changed"*. `covered_by:`'s silent rot for the second time
    in one tool. The identity that matters is *a machine said this*, not
    *which machine*.
    """
    from project_os_cockpit import ledger as _ledger

    declared: dict[str, list[str]] = {}
    for decl in _scanner().scan(root):
        declared.setdefault(decl.check, []).append(decl.test)

    passing: dict[str, list[str]] = {}
    failing: dict[str, list[str]] = {}
    for check, tests in sorted(declared.items()):
        seen = [t for t in tests if t in results]
        if not seen:
            continue
        bad = sorted(t for t in seen if not results[t])
        if bad:
            failing[check] = bad
        else:
            passing[check] = sorted(seen)

    current = _ledger.verdicts(root / "docs", platform)
    stale = sorted(
        check for check, verdict in current.items()
        if verdict.method == "automated"
        and check not in passing and check not in failing
    )
    return passing, failing, stale, current


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--junit", required=True)
    ap.add_argument("--platform", required=True)
    ap.add_argument("--by", default="ci")
    ap.add_argument("--run", default="", help="what identifies this run, "
                                              "recorded on an invalidation")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.repo_root).resolve()

    from project_os_cockpit import ledger as _ledger

    results = junit_results(Path(args.junit))
    passing, failing, stale, current = plan(root, results, args.platform)
    run = args.run or "the test run"

    wrote: list[str] = []
    for check, tests in sorted(passing.items()):
        standing = current.get(check)
        #: Only when the answer changes. An identical re-append records
        #: nothing and `resolve()` returns the same verdict either way.
        #:
        #: **Not keyed on `by` either**, for the same reason `stale` is not:
        #: a machine already says pass, and a second machine saying pass adds
        #: no information. Keying on it appended one entry per CI-job rename.
        if (standing is not None and standing.mark == "pass"
                and standing.method == "automated"):
            continue
        wrote.append("pass %s (%s)" % (check, ", ".join(tests)))
        if not args.dry_run:
            _ledger.append(root / "docs", args.platform, check=check,
                           mark="pass", by=args.by, method="automated",
                           reason="observed by %s in %s" % (
                               ", ".join(tests), run))
    #: **A failing test invalidates whoever wrote the standing verdict**, and
    #: the asymmetry with `stale` above is a decision rather than an
    #: oversight. The run OBSERVED the covering test fail, which is evidence
    #: about the CHECK — a person's walk from March does not survive a
    #: machine watching the behaviour break today. `stale` retracts only
    #: machine claims because it observed nothing at all, and a run that saw
    #: nothing has nothing to say about a person's walk.
    #:
    #: The docstring claimed the opposite for one commit while the code did
    #: this; independent review constructed a `method: manual` verdict and
    #: watched it be invalidated. The behaviour was right, the sentence was
    #: wrong, and the sentence is what changed.
    for check, tests in sorted(failing.items()):
        if check not in current:
            continue
        wrote.append("invalidate %s (failing: %s)" % (check, ", ".join(tests)))
        if not args.dry_run:
            _ledger.append(root / "docs", args.platform, check=check,
                           invalidated_by=run,
                           reason="covering test failed: %s" % ", ".join(tests))
    for check in stale:
        wrote.append("invalidate %s (no covering test observed)" % check)
        if not args.dry_run:
            _ledger.append(root / "docs", args.platform, check=check,
                           invalidated_by=run,
                           reason="declared covered, and no covering test ran "
                                  "in this run — the declaration was deleted, "
                                  "renamed or disabled")

    if not wrote:
        print("emit-coverage: nothing changed (%d check(s) observed passing)"
              % len(passing))
        return 0
    for line in wrote:
        print("emit-coverage: %s%s" % ("(dry-run) " if args.dry_run else "", line))
    return 0


if __name__ == "__main__":                            # pragma: no cover
    raise SystemExit(main())
