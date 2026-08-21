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


def _junit(tmp: Path, cases: dict[str, str]) -> Path:
    """`{test name: ''|'failure'|'skipped'}` as a JUnit report."""
    body = ""
    for name, outcome in cases.items():
        inner = f"<{outcome} message='x'/>" if outcome else ""
        body += f"<testcase classname='m' name='{name}'>{inner}</testcase>"
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
                           {"test_the_thing": "", "test_second": "failure"}))
    assert _blocking(tmp_path) == {"TST-0001"}


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    from project_os_cockpit import ledger

    _repo(tmp_path)
    out = _emit(tmp_path, _junit(tmp_path, {"test_the_thing": ""}), "--dry-run")
    assert "(dry-run)" in out.stdout
    assert ledger.load(tmp_path / "docs", "macos")[0].entries == []


def test_it_does_not_push(tmp_path: Path) -> None:
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
