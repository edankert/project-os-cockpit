"""Coverage is observed, not declared ([[FEAT-0138]] / [[TASK-0542]]/[[TASK-0543]]).

**The dependency inverts.** `covered_by:` on the check was a standing claim
and it rots silently: rename, delete or `@Ignore` the covering test and the
note keeps asserting coverage while the check drops out of the run list
permanently, with no signal. That is worse than a stale verdict, because a
stale verdict still asks.

The proof this whole feature exists for is
`test_deleting_the_covering_test_puts_its_check_back_on_the_run_list` — and it
is constructed and executed here rather than argued.

**The limit is stated rather than papered over** ([[ISS-0209]]): the
acceptance gate runs in no repo that holds a check, so the emitter runs here
and nowhere the data lives. Everything below is proved in
`project-os-cockpit`. The fleet is not covered and this does not claim it is.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "tools" / "scripts" / "coverage-declarations.py"
EMITTER = ROOT / "tools" / "scripts" / "emit-coverage.py"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"),
                                                  path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cd = _load(SCANNER)


JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="{n}">{cases}</testsuite></testsuites>
"""


def _junit(tmp: Path, cases: dict[str, str], classname: str = "tests.test_thing",
           classes: "dict[str, str] | None" = None) -> Path:
    """`{test name: ''|'failure'|'skipped'}` as a JUnit report.

    `classname` defaults to the module the fixture's declaring test lives in,
    because the emitter matches a declaration against it — a bare name is not
    unique across a suite, and this repo had a live collision.
    """
    body = ""
    for name, outcome in cases.items():
        inner = f"<{outcome} message='x'/>" if outcome else ""
        cls = (classes or {}).get(name, classname)
        body += f"<testcase classname='{cls}' name='{name}'>{inner}</testcase>"
    path = tmp / "junit.xml"
    path.write_text(JUNIT.format(n=len(cases), cases=body), encoding="utf-8")
    return path


def _repo(tmp: Path, *, declares: str = "TST-0001",
          test_name: str = "test_the_thing") -> Path:
    (tmp / "docs" / "tests" / "acceptance").mkdir(parents=True, exist_ok=True)
    (tmp / "docs" / "releases" / "ledgers").mkdir(parents=True, exist_ok=True)
    (tmp / "tests").mkdir(parents=True, exist_ok=True)
    (tmp / "docs" / "tests" / "acceptance" / "TST-0001-C.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0001\ntitle: "A check"\n'
        'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
        'covers: ["[[FEAT-0001]]"]\n---\n\n# A check\n', encoding="utf-8")
    (tmp / "docs" / "releases" / "ledgers" / "WORKING-macos.json").write_text(
        '{"platform": "macos", "entries": [], "evidence": []}', encoding="utf-8")
    if declares:
        (tmp / "tests" / "test_thing.py").write_text(
            f"def {test_name}():\n"
            f"    # Covers: {declares}\n"
            f"    assert True\n", encoding="utf-8")
    return tmp


def _emit(tmp: Path, junit: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(EMITTER), "--repo-root", str(tmp),
         "--junit", str(junit), "--platform", "macos", "--by", "ci:test",
         "--run", "run-1", *extra],
        capture_output=True, text=True, cwd=ROOT)


def _blocking(tmp: Path) -> set[str]:
    from project_os_cockpit import acceptance
    from project_os_cockpit.index import Index

    docs = tmp / "docs"
    suite = acceptance.load(docs, index=Index.build(docs), platform="macos")
    return {i.note_id for i in suite.blocking()}


# ---- TASK-0542: the declaration --------------------------------------------

def test_one_grep_finds_every_declaration(tmp_path: Path) -> None:
    """*"findable by one grep"* is the convention's whole requirement, so it is
    asserted with a grep rather than with the parser that consumes it."""
    _repo(tmp_path)
    out = subprocess.run(["grep", "-rn", "Covers: TST-", str(tmp_path / "tests")],
                         capture_output=True, text=True)
    assert "TST-0001" in out.stdout


def test_the_declaration_names_its_test(tmp_path: Path) -> None:
    _repo(tmp_path)
    found = cd.scan(tmp_path)
    assert [(d.check, d.test) for d in found] == [("TST-0001", "test_the_thing")]


@pytest.mark.parametrize("suffix,body,expected", [
    (".py", "def test_x():\n    # Covers: TST-0001\n", "test_x"),
    (".kt", "fun myCheck() {\n    // Covers: TST-0001\n}\n", "myCheck"),
    (".java", "public void myCheck() {\n    // Covers: TST-0001\n}\n", "myCheck"),
    (".swift", "func testX() {\n    // Covers: TST-0001\n}\n", "testX"),
])
def test_it_works_in_both_toolchains_without_a_shared_library(
        tmp_path: Path, suffix: str, body: str, expected: str) -> None:
    """[[TASK-0542]]: *"It works in this repo (pytest) and in `your-trainer`
    (JVM) without a shared library — a v1 that needs one ships nowhere."*
    One comment prefix per language; no annotation, no dependency."""
    d = tmp_path / expected
    d.mkdir()
    (d / f"a{suffix}").write_text(body, encoding="utf-8")
    found = cd.scan(d)
    assert [(x.check, x.test) for x in found] == [("TST-0001", expected)]


def test_a_declaration_in_a_string_is_not_a_declaration(tmp_path: Path) -> None:
    """**The failure this scanner was built wrong for once.** The first cut
    asked whether `#` appeared before the marker on the line — and a `#`
    comment *inside a docstring* satisfies that, so the tool read its own usage
    example and reported two coverage claims for a test it had never seen.

    Python is handled by `tokenize` and `ast` for exactly this reason.
    """
    (tmp_path / "a.py").write_text(
        'DOC = """\n'
        'def test_documented():\n'
        '    # Covers: TST-0001\n'
        '"""\n'
        'def test_real():\n'
        '    # Covers: TST-0001\n'
        '    pass\n', encoding="utf-8")
    found = cd.scan(tmp_path)
    assert [(d.check, d.test) for d in found] == [("TST-0001", "test_real")], found


def test_a_declaration_outside_a_test_is_refused(tmp_path: Path) -> None:
    """A marker nothing runs can never stop emitting, which is the entire
    mechanism. Attributing it to whatever happens to be near it would put the
    guess back in."""
    _repo(tmp_path, declares="")
    (tmp_path / "tests" / "loose.py").write_text(
        "# Covers: TST-0001\ndef helper():\n    pass\n", encoding="utf-8")
    found = cd.problems(tmp_path)
    assert len(found) == 1 and "outside any test" in found[0], found


def test_a_declaration_naming_no_check_is_refused(tmp_path: Path) -> None:
    """Coverage of a check that does not exist is a verdict about nothing."""
    _repo(tmp_path, declares="TST-9999")
    found = cd.problems(tmp_path)
    assert len(found) == 1 and "not an acceptance check" in found[0], found


def test_a_clean_repo_says_nothing(tmp_path: Path) -> None:
    _repo(tmp_path)
    assert cd.problems(tmp_path) == []


def test_this_repos_own_declarations_check_out() -> None:
    """Run against the real corpus, not a fixture: the tool is only useful if
    it is true of the repo that ships it."""
    out = subprocess.run(
        [sys.executable, str(SCANNER), "--repo-root", str(ROOT), "--check"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


# ---- TASK-0543: the emitter ------------------------------------------------

def test_a_green_run_appends_one_automated_entry_per_covered_check(
        tmp_path: Path) -> None:
    from project_os_cockpit import ledger

    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    entries = ledger.load(tmp_path / "docs", "macos")[0].entries
    assert len(entries) == 1
    assert entries[0].check == "TST-0001"
    assert entries[0].mark == "pass"
    assert entries[0].method == "automated"
    assert entries[0].by == "ci:test"
    assert "test_the_thing" in entries[0].reason


def test_it_appends_only_when_the_answer_changes(tmp_path: Path) -> None:
    """The ledger is an event log and an event is a change. An identical
    re-append on every green run grows the file and records nothing."""
    from project_os_cockpit import ledger

    _repo(tmp_path)
    junit = _junit(tmp_path, {"test_the_thing": ""})
    _emit(tmp_path, junit)
    out = _emit(tmp_path, junit)
    assert "nothing changed" in out.stdout, out.stdout
    assert len(ledger.load(tmp_path / "docs", "macos")[0].entries) == 1


def test_a_failing_covering_test_invalidates_rather_than_emitting_fail(
        tmp_path: Path) -> None:
    """**[[TASK-0543]]'s explicit decision.** `mark: fail` is a *walk* verdict
    in the blocking vocabulary, so emitting it would put a machine-driven
    population straight into the release gate — the change [[ADR-0031]]
    recorded as a risk. An invalidation says what is true: the evidence no
    longer holds.

    And emitting **nothing** — the other named option — was rejected because it
    leaves the last green run's `pass` standing over a test that now fails.
    """
    from project_os_cockpit import ledger

    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    assert _blocking(tmp_path) == set(), "a green run should settle the check"

    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "failure"}))
    entries = ledger.load(tmp_path / "docs", "macos")[0].entries
    assert len(entries) == 2
    assert entries[1].is_invalidation, entries[1]
    assert entries[1].mark == "", "a fail verdict was emitted"
    assert _blocking(tmp_path) == {"TST-0001"}


def test_deleting_the_covering_test_puts_its_check_back_on_the_run_list(
        tmp_path: Path) -> None:
    """**The criterion this whole feature exists for** ([[TASK-0543]] 4,
    [[REQ-0057]] 4).

    Under the standing claim the note kept asserting coverage and the check
    left the run list *permanently, with no signal*. Under observed coverage
    the run simply stops seeing it and says so.

    Constructed and executed: settle it by a run, delete the test, run again.
    """
    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    assert _blocking(tmp_path) == set()

    #: The deletion. Nothing in `docs/` is touched — that is the point.
    (tmp_path / "tests" / "test_thing.py").unlink()

    _emit(tmp_path, _junit(tmp_path, {"test_something_else": ""}))
    assert _blocking(tmp_path) == {"TST-0001"}, (
        "the check stayed settled after its only covering test was deleted — "
        "which is exactly the silent rot `covered_by:` had"
    )


def test_disabling_the_covering_test_does_the_same(tmp_path: Path) -> None:
    """`@Ignore` is the case [[FEAT-0138]] names beside delete and rename, and
    a skipped test is *not observed* — so it is absent from the results rather
    than present and true."""
    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    assert _blocking(tmp_path) == set()
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "skipped"}))
    assert _blocking(tmp_path) == {"TST-0001"}


def test_a_check_the_ledger_never_heard_of_is_not_invalidated(
        tmp_path: Path) -> None:
    """There is no standing verdict to overtake, and appending an invalidation
    would be an event about nothing. Absence already means owed ([[REQ-0054]]).
    """
    from project_os_cockpit import ledger

    _repo(tmp_path)
    out = _emit(tmp_path, _junit(tmp_path, {"test_something_else": ""}))
    assert ledger.load(tmp_path / "docs", "macos")[0].entries == []
    assert "nothing changed" in out.stdout, out.stdout


def test_every_declaring_test_must_pass(tmp_path: Path) -> None:
    """A check covered by five tests is covered by all five. Reporting it as
    passing because four did is the overclaiming this phase exists to remove."""
    _repo(tmp_path)
    (tmp_path / "tests" / "test_two.py").write_text(
        "def test_second():\n    # Covers: TST-0001\n    pass\n",
        encoding="utf-8")
    _emit(tmp_path, _junit(tmp_path,
                           {"test_the_thing": "", "test_second": "failure"},
                           classes={"test_second": "tests.test_two"}))
    assert _blocking(tmp_path) == {"TST-0001"}


def test_renaming_the_ci_job_does_not_strand_prior_verdicts(
        tmp_path: Path) -> None:
    """**The second time `covered_by:`'s silent rot appeared in this tool.**

    `plan` filtered the invalidation set on `verdict.by == by`, so renaming the
    CI job made the run stop recognising its own prior claims: delete the
    covering test, run under a new `--by`, and the output reads *"nothing
    changed"* while the check stays settled with nothing covering it.

    Found by independent review, 2026-08-21, by constructing exactly this. The
    identity that matters is *a machine said this*, not *which machine*.
    """
    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    assert _blocking(tmp_path) == set()

    (tmp_path / "tests" / "test_thing.py").unlink()
    out = subprocess.run(
        [sys.executable, str(EMITTER), "--repo-root", str(tmp_path),
         "--junit", str(_junit(tmp_path, {"other": ""})),
         "--platform", "macos", "--by", "ci:renamed", "--run", "run-2"],
        capture_output=True, text=True, cwd=ROOT)
    assert "nothing changed" not in out.stdout, out.stdout
    assert _blocking(tmp_path) == {"TST-0001"}, (
        "renaming the CI job stranded the verdict it had written — the check "
        "stayed settled with no covering test in the repo"
    )


def test_a_run_that_observed_nothing_does_not_retract_a_persons_walk(
        tmp_path: Path) -> None:
    """`stale` retracts **machine claims only**. A person's `manual` walk and a
    `migration` backfill are not the emitter's to take back when it observed
    nothing about them: a run that saw nothing has nothing to say."""
    from project_os_cockpit import ledger

    for method, by in (("manual", "user:edwin"), ("migration", "migration")):
        root = _repo(tmp_path / method, declares="")
        ledger.append(root / "docs", "macos", check="TST-0001", mark="pass",
                      by=by, method=method, reason="walked it")
        assert _blocking(root) == set()
        _emit(root, _junit(root, {"unrelated": ""}))
        assert _blocking(root) == set(), (
            f"a run that observed nothing retracted a {method} verdict"
        )
        assert len(ledger.load(root / "docs", "macos")[0].entries) == 1


def test_a_failing_test_invalidates_a_persons_walk_too(tmp_path: Path) -> None:
    """**And this asymmetry is the decision.** The run OBSERVED the covering
    test fail, which is evidence about the check — a walk from March does not
    survive a machine watching the behaviour break today.

    The docstring claimed the opposite for one commit while the code did this.
    Independent review constructed the case; the behaviour was right and the
    sentence was wrong.
    """
    from project_os_cockpit import ledger

    _repo(tmp_path)
    ledger.append(tmp_path / "docs", "macos", check="TST-0001", mark="pass",
                  by="user:edwin", method="manual", reason="walked it")
    assert _blocking(tmp_path) == set()
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "failure"}))
    assert _blocking(tmp_path) == {"TST-0001"}
    assert ledger.load(tmp_path / "docs", "macos")[0].entries[-1].is_invalidation


def test_two_runs_covering_different_toolchains_do_not_retract_each_other(
        tmp_path: Path) -> None:
    """**The hole the first fix opened, and it recurs where the one it closed
    was a one-off.**

    Removing the `--by` filter made `stale` *every automated verdict this run
    did not re-observe*. Independent review constructed the consequence on the
    two toolchains this tool exists to serve: a `.py` run and a `.kt` run on
    one platform retract each other **forever**, two ledger entries per run,
    growing without bound.

    Absence is only evidence when the **declaration** is gone. A test that was
    simply not part of this run keeps its verdict.
    """
    from project_os_cockpit import ledger

    root = _repo(tmp_path, declares="")
    (root / "docs" / "tests" / "acceptance" / "TST-0002-C.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0002\ntitle: "Another check"\n'
        'level: acceptance\nstatus: active\narea: "A"\nmark: todo\n'
        'covers: ["[[FEAT-0001]]"]\n---\n\n# Another check\n', encoding="utf-8")
    (root / "tests" / "test_py.py").write_text(
        "def test_python_side():\n    # Covers: TST-0001\n    assert True\n",
        encoding="utf-8")
    (root / "tests" / "Kt.kt").write_text(
        "fun kotlinSide() {\n    // Covers: TST-0002\n}\n", encoding="utf-8")

    for _ in range(3):
        _emit(root, _junit(root, {"test_python_side": ""}, classname="tests.test_py"))
        _emit(root, _junit(root, {"kotlinSide": ""}, classname="Kt"))

    entries = ledger.load(root / "docs", "macos")[0].entries
    assert [e.check for e in entries] == ["TST-0001", "TST-0002"], (
        "the two runs are retracting each other: %s"
        % [(e.check, e.is_invalidation) for e in entries]
    )
    assert _blocking(root) == set()


def test_a_second_machine_saying_pass_adds_nothing(tmp_path: Path) -> None:
    """The other half of the `--by` removal, which was guarded by nothing:
    restoring `standing.by == args.by` in the pass-dedup failed no test at all.

    A machine already says pass; a differently-named machine saying pass is
    not a new fact, and appending one entry per CI-job rename is the growth
    the event log exists to avoid."""
    from project_os_cockpit import ledger

    _repo(tmp_path)
    junit = _junit(tmp_path, {"test_the_thing": ""})
    _emit(tmp_path, junit)
    out = subprocess.run(
        [sys.executable, str(EMITTER), "--repo-root", str(tmp_path),
         "--junit", str(junit), "--platform", "macos",
         "--by", "ci:renamed", "--run", "run-2"],
        capture_output=True, text=True, cwd=ROOT)
    assert "nothing changed" in out.stdout, out.stdout
    assert len(ledger.load(tmp_path / "docs", "macos")[0].entries) == 1


def test_a_run_that_never_reached_the_test_leaves_it_alone(
        tmp_path: Path) -> None:
    """Absent from the report is *this run was not about that test*; skipped is
    *this run reached it and declined to produce evidence*. Only the second is
    `@Ignore`, and only the second withdraws the verdict."""
    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    assert _blocking(tmp_path) == set()
    #: A partial run — one unrelated test — must not touch it.
    _emit(tmp_path, _junit(tmp_path, {"test_unrelated": ""}))
    assert _blocking(tmp_path) == set()
    #: Reached and skipped: withdrawn.
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "skipped"}))
    assert _blocking(tmp_path) == {"TST-0001"}


def test_a_skipped_test_invalidates_once_not_once_per_run(
        tmp_path: Path) -> None:
    """**The repair for the toolchain hole reopened the same unbounded growth
    one branch over.**

    The skipped branch iterated `declared` and consulted neither the ledger nor
    what it had already written, so an `@Ignore`d test produced one
    invalidation **per run** — and an `@Ignore` sits for weeks while CI runs on
    every push. Independent review ran it four times and counted four.

    The set is read off `current` now, so an invalidation clears the verdict
    and the check leaves the set on the next run by construction. The module's
    own invariant — *it appends only when the answer changes* — holds for this
    branch too.
    """
    from project_os_cockpit import ledger

    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    for _ in range(4):
        _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "skipped"}))
    entries = ledger.load(tmp_path / "docs", "macos")[0].entries
    assert len(entries) == 2, [(e.check, e.is_invalidation) for e in entries]
    assert entries[1].is_invalidation
    assert _blocking(tmp_path) == {"TST-0001"}


def test_a_check_with_no_verdict_is_never_invalidated(tmp_path: Path) -> None:
    """An invalidation with no standing verdict is an event about nothing.
    Absence already means owed ([[REQ-0054]]) — and this held for the *absent*
    case from the start while the *skipped* case wrote three in three runs."""
    from project_os_cockpit import ledger

    _repo(tmp_path)
    for _ in range(3):
        _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "skipped"}))
    assert ledger.load(tmp_path / "docs", "macos")[0].entries == []


def test_a_skipped_sibling_is_not_laundered_into_a_pass(
        tmp_path: Path) -> None:
    """A check covered by two tests is covered by both. One passing and one
    `@Ignore`d is half an answer, and `emit-coverage: pass` was what came out.

    `test_every_declaring_test_must_pass` exercised only the *failing* sibling,
    which is the cell that happened to be right.
    """
    _repo(tmp_path)
    (tmp_path / "tests" / "test_two.py").write_text(
        "def test_second():\n    # Covers: TST-0001\n    pass\n",
        encoding="utf-8")
    out = _emit(tmp_path, _junit(
        tmp_path, {"test_the_thing": "", "test_second": "skipped"},
        classes={"test_second": "tests.test_two"}))
    assert "pass TST-0001" not in out.stdout, out.stdout
    assert _blocking(tmp_path) == {"TST-0001"}


def test_two_tests_with_one_name_are_not_the_same_test(
        tmp_path: Path) -> None:
    """**The collision was live in this repo when it was found.**
    `test_it_does_not_push` existed in `test_close_out_commit.py`, declaring
    [[TST-0069]], and in `test_observed_coverage.py`, declaring nothing. CI
    runs both into one report, so the non-declaring twin failing invalidated
    the other's verdict.

    `classname` is in the XML and was not being read. Now it is: a declaration
    matches the report entry from **its own file**.
    """
    _repo(tmp_path)
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}))
    assert _blocking(tmp_path) == set()

    #: A same-named test in a different module, failing. It is a different
    #: test and it says nothing about this check.
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "failure"},
                           classname="tests.some_other_module"))
    assert _blocking(tmp_path) == set(), (
        "a same-named test in another module invalidated this check's verdict"
    )


def test_a_report_that_does_not_name_the_file_emits_nothing(
        tmp_path: Path) -> None:
    """Fail-closed, and there is deliberately no bare-name fallback. Two report
    entries carry the declaring test's name and neither `classname` identifies
    its file — so the run did not cover it, and the emitter says nothing rather
    than picking whichever sorted first."""
    from project_os_cockpit import ledger

    _repo(tmp_path)
    junit = tmp_path / "amb.xml"
    junit.write_text(
        "<testsuites><testsuite name='x' tests='2'>"
        "<testcase classname='a.b' name='test_the_thing'/>"
        "<testcase classname='c.d' name='test_the_thing'/>"
        "</testsuite></testsuites>", encoding="utf-8")
    _emit(tmp_path, junit)
    assert ledger.load(tmp_path / "docs", "macos")[0].entries == []


def test_one_check_gets_at_most_one_invalidation_per_run(
        tmp_path: Path) -> None:
    """A run where one declaring test fails and another is skipped hits both
    branches. The `failing` loop writes the entry; `_withdrawn` must decline.

    Guarded by nothing until independent review mutated that line to
    `if False:` and watched a second `invalidate` appear on the same check in
    the same run — passing all 34 tests in this file.
    """
    from project_os_cockpit import ledger

    _repo(tmp_path)
    (tmp_path / "tests" / "test_two.py").write_text(
        "def test_second():\n    # Covers: TST-0001\n    pass\n",
        encoding="utf-8")
    _emit(tmp_path, _junit(tmp_path, {"test_the_thing": "", "test_second": ""},
                           classes={"test_second": "tests.test_two"}))
    _emit(tmp_path, _junit(
        tmp_path, {"test_the_thing": "failure", "test_second": "skipped"},
        classes={"test_second": "tests.test_two"}))
    entries = ledger.load(tmp_path / "docs", "macos")[0].entries
    assert len(entries) == 2, [(e.check, e.is_invalidation) for e in entries]
    assert entries[1].is_invalidation


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    from project_os_cockpit import ledger

    _repo(tmp_path)
    out = _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}), "--dry-run")
    assert "(dry-run)" in out.stdout
    assert ledger.load(tmp_path / "docs", "macos")[0].entries == []


def test_the_emitter_does_not_push(tmp_path: Path) -> None:
    """A commit is local and reversible; a push is publishing. This writes the
    working ledger and stops — landing the entries is a person's commit, like
    every other write in this repo."""
    src = EMITTER.read_text(encoding="utf-8")
    for forbidden in ("git push", "subprocess", "os.system"):
        assert forbidden not in src, forbidden


def test_nothing_declares_coverage_in_a_note() -> None:
    """[[REQ-0057]] criterion 1, asserted over the real corpus.

    **Frontmatter, not prose.** Twenty notes discuss `covered_by:` — this
    phase's own argument is largely about it — and a text match reports every
    one of them, which is the over-broad assertion this phase has now hit six
    times. The claim is only a claim when it is a FIELD.
    """
    import yaml

    hits = []
    for path in (ROOT / "docs").rglob("*.md"):
        if "__templates__" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---") or text.count("---") < 2:
            continue
        try:
            fm = yaml.safe_load(text.split("---", 2)[1]) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(fm, dict):
            continue
        if fm.get("covered_by"):
            hits.append(path.relative_to(ROOT).as_posix())
    assert hits == [], hits


# ---- the run that does the observing ---------------------------------------

WORKFLOW = ROOT / ".github" / "workflows" / "observed-coverage.yml"


def test_a_ci_run_emits_into_the_working_ledger() -> None:
    """[[TASK-0543]] 1 and [[REQ-0057]] 3. Asserted on the workflow, because a
    tool nothing invokes is [[ISS-0249]]'s shape — a complete capability no
    front door reaches."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "emit-coverage.py" in text
    assert "--junitxml=junit.xml" in text
    assert "coverage-declarations.py" in text


def test_the_emitting_step_runs_even_when_the_suite_fails() -> None:
    """A failing run has something to say: a covering test that fails
    invalidates its check's standing verdict, which is what puts the check
    back on the run list. Gating the emitter on green would lose exactly that.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    i = text.index("Emit what the run observed")
    assert "if: always()" in text[i:i + 400], text[i:i + 400]


def test_the_platform_comes_from_the_runs_target() -> None:
    """[[TASK-0543]] criterion 3. Emitting `macos` verdicts from a linux runner
    would be a false statement about where the evidence came from."""
    text = WORKFLOW.read_text(encoding="utf-8")
    i = text.index("  observe:")
    block = text[i:]
    assert "runs-on: macos-latest" in block
    assert "--platform macos" in block


def test_ci_does_not_push_the_ledger() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "git push" not in text
    assert "never pushed" in text
