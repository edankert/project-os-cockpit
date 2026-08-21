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


def junit_results(
    path: Path,
) -> "tuple[dict[tuple[str, str], bool], set[tuple[str, str]]]":
    """`({(classname, test): passed}, {(classname, test) skipped})`.

    Keyed on **both**, because a bare test name is not unique across a suite —
    see the comment below. pytest writes the module in `classname` and gradle
    writes the fully-qualified class; either is enough to tell two same-named
    tests apart.
    """
    out: dict[tuple[str, str], bool] = {}
    skipped: set[tuple[str, str]] = set()
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        name = str(case.get("name") or "").strip()
        if not name:
            continue
        #: **`classname` is read, and not reading it was a live defect.**
        #: Keying on the bare name ANDed two different tests together: this
        #: repo has `test_it_does_not_push` in `test_close_out_commit.py`
        #: (which declares TST-0069) and in `test_observed_coverage.py` (which
        #: declares nothing), CI runs both into one report, and the
        #: non-declaring twin failing invalidated the other's verdict. Found by
        #: independent review, fourth pass, by constructing the shape.
        where = str(case.get("classname") or "").strip()
        #: pytest parametrisation writes `test_x[param]`; the declaration
        #: names the function, so the parameter is stripped and every case
        #: must pass for the check to be observed passing.
        base = name.split("[", 1)[0]
        key = (where, base)
        if case.find("skipped") is not None:
            #: **Skipped is observed, and it is not a pass.** `@Ignore` is the
            #: case FEAT-0138 names beside delete and rename. It is kept
            #: SEPARATE from absence because the two mean different things: a
            #: skipped test says *this run declined to produce evidence*, and
            #: an absent one says *this run was not about that test at all*.
            skipped.add(key)
            continue
        ok = all(case.find(tag) is None for tag in ("failure", "error"))
        out[key] = out.get(key, True) and ok
    return out, skipped


def plan(root: Path, results: dict[str, bool], skipped: "set[str]",
         platform: str):
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

    #: Each declaration carries the file it is in, so it can be matched
    #: against the report's `classname` rather than on the bare name alone.
    declared: dict[str, list[tuple[str, str]]] = {}
    for decl in _scanner().scan(root):
        declared.setdefault(decl.check, []).append((decl.rel, decl.test))

    def _resolve(where: str, test: str) -> "tuple[str, str] | None":
        """The report key for one declaration, or `None` when the run did not
        cover it — or covered it unattributably.

        **Three tiers, best first, and a tie in the best tier is a refusal.**

        1. the `classname` IS the declaration's module, or is nested inside it
           (`tests.test_x`, and `tests.test_x.TestGroup` for a test in a class);
        2. the `classname`'s last component is the declaration's file stem,
           which is the JVM (`com.x.FooTest`) and XCTest shape;
        3. nothing — the run did not cover it.

        **Tier 1 must be exhausted before tier 2 is consulted.** Two files
        called `test_thing.py` in different directories both satisfy tier 2 for
        each other, and the first version took whichever came first in the
        report — so the same two entries in the other order gave a different
        answer. Order-dependence in a rule about evidence is not a rule.

        **A tie is `None`, and `None` is not "the test was deleted".** Round
        four folded unresolvable into *absent from this run*, and wrapping a
        declaring test in a class silently stopped every emission: pytest
        writes `classname="tests.test_thing.TestGroup"`, tier 1's equality
        failed, tier 2's stem test failed, and the output read *"nothing
        changed"* on every run thereafter. Present-and-unattributable is a
        third state; it emits nothing in either direction and `main` says so.
        """
        stem = where.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        dotted = where.rsplit(".", 1)[0].replace("/", ".")
        keys = [k for k in list(results) + sorted(skipped) if k[1] == test]
        exact = [k for k in keys
                 if k[0] == dotted or k[0].startswith(dotted + ".")]
        if len(exact) == 1:
            return exact[0]
        if exact:
            return None
        loose = [k for k in keys
                 if k[0] == stem or k[0].rsplit(".", 1)[-1] == stem]
        return loose[0] if len(loose) == 1 else None

    def _ambiguous(where: str, test: str) -> bool:
        """Present in the report and not attributable to this declaration.

        Reported rather than silent: a run that saw a test it cannot place is
        a fact about the run, and the whole point of observed coverage is that
        nothing is asserted about a check nobody watched.
        """
        return (_resolve(where, test) is None
                and any(k[1] == test for k in list(results) + sorted(skipped)))

    passing: dict[str, list[str]] = {}
    failing: dict[str, list[str]] = {}
    #: **A skipped sibling is not laundered into a pass.** A check covered by
    #: five tests is covered by all five; four passing and one `@Ignore`d is
    #: four fifths of an answer, and reporting it as `pass` is the
    #: overclaiming this phase spent itself removing. Independent review
    #: constructed exactly that and watched `pass` come out.
    resolved: dict[str, list[tuple[str, str] | None]] = {
        check: [_resolve(where, test) for where, test in tests]
        for check, tests in sorted(declared.items())
    }
    unattributable = sorted(
        "%s (%s in %s)" % (check, test, where)
        for check, tests in sorted(declared.items())
        for where, test in tests if _ambiguous(where, test)
    )
    for check, keys in resolved.items():
        seen = [k for k in keys if k is not None and k in results]
        held = [k for k in keys if k is not None and k in skipped]
        bad = sorted(k[1] for k in seen if not results[k])
        if bad:
            failing[check] = bad
        elif seen and not held:
            passing[check] = sorted(k[1] for k in seen)

    current = _ledger.verdicts(root / "docs", platform)

    def _withdrawn(check: str) -> bool:
        """Has the machine's claim on this check stopped being backed?

        Two ways, and they are different facts:

        * **no test declares it any more** -- deleted, renamed away, moved out;
        * **every declaring test ran and at least one was skipped** -- the run
          reached them and declined to produce evidence, which is `@Ignore`.

        A declaring test simply ABSENT from this run's report is neither: a
        partial run is not evidence of absence, and treating it as one made a
        `.py` run and a `.kt` run retract each other on every cycle.
        """
        keys = resolved.get(check)
        if not keys:
            return True
        #: **Two invalidations for one check in one run is one too many.**
        #: A run where one declaring test fails and another is skipped hits
        #: both branches, and the `failing` loop writes its own entry.
        #: Independent review mutated this line to `if False:` and watched a
        #: second `invalidate` appear on the same check in the same run.
        if check in passing or check in failing:
            return False
        return (any(k in skipped for k in keys if k is not None)
                and all(k is not None and (k in skipped or k in results)
                        for k in keys))

    #: **Read off `current`, so it appends only when the answer changes.**
    #: The first cut iterated `declared` for the skipped case and consulted
    #: neither the ledger nor what it had already written -- so an `@Ignore`d
    #: test produced one invalidation **per run, forever** (an `@Ignore` sits
    #: for weeks while CI runs on every push), and a check with no verdict at
    #: all produced invalidations of nothing. Reading `current` closes both:
    #: an invalidation clears the verdict, so the check leaves this set on the
    #: next run by construction. Found by independent review, third pass.
    stale = sorted(
        check for check, verdict in current.items()
        if verdict.method == "automated" and _withdrawn(check)
    )
    return passing, failing, stale, current, unattributable


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

    results, skipped = junit_results(Path(args.junit))
    passing, failing, stale, current, unattributable = plan(
        root, results, skipped, args.platform)
    for note in unattributable:
        print("emit-coverage: NOT ATTRIBUTED %s — the run holds a test with "
              "that name and no classname identifying the declaration's file; "
              "nothing emitted in either direction" % note)
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
        wrote.append("invalidate %s (no covering test declares it)" % check)
        if not args.dry_run:
            _ledger.append(root / "docs", args.platform, check=check,
                           invalidated_by=run,
                           reason="a machine claimed to cover this and no test "
                                  "declares it any more, or every declaring "
                                  "test was skipped — the declaration was "
                                  "deleted, renamed away or disabled")

    if not wrote:
        print("emit-coverage: nothing changed (%d check(s) observed passing)"
              % len(passing))
        return 0
    for line in wrote:
        print("emit-coverage: %s%s" % ("(dry-run) " if args.dry_run else "", line))
    return 0


if __name__ == "__main__":                            # pragma: no cover
    raise SystemExit(main())
