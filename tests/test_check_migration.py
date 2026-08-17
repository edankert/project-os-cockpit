"""Nothing is lost when a suite becomes notes (TASK-0460 / TASK-0461 / TASK-0462).

The migration's only real risk is a silent one: a row that does not arrive, a
mark that arrives as a different mark, a gate that reports a smaller number than
the document held. [[ISS-0175]] is this project's record of what assuming
costs — a mapping that "obviously" held drifted by 37 rows on the one corpus it
ran against, and 285 of 542 rendered rows carried another row's text for eleven
days before anybody noticed.

So the assertions here are about **equality between the two shapes**, measured
by running the real migration over a real suite and reading the result back
through the real loader.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import acceptance

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_DOCS = REPO_ROOT / "docs"
SCRIPT = REPO_ROOT / "tools" / "scripts" / "migrate-acceptance-checks.py"

#: A suite with one of everything the parser classifies differently, plus the
#: two shapes of `RE-RUN` annotation the fleet actually writes (28 at the end
#: of the line, 26 mid-sentence). Built rather than borrowed: this repo's own
#: suite has already migrated, and a fixture that reads the live corpus would
#: stop exercising the file shape the day the last repo left it.
SUITE = """---
type: "[[reference]]"
id: ACCEPTANCE-TESTS
title: "Acceptance test suite"
status: active
created: 2026-01-01
---

# Acceptance Test Suite: probe

## Rules

1. New feature implemented -> add Tier 1 test(s).

# Tier 1 — Feature Tests

## 1.1 The navigator ([[FEAT-0001]], FEAT-0002)
- [x] **Walked:** open it and expect the tray. — 2026-08-10: it was there.
- [ ] **Unwalked:** nobody has done this one.
- [~] **Reconciled:** the surface was retired — cut by decision.
- [x] **Annotated at the end:** open the screen. RE-RUN (TASK-0385: the screen was replaced)
- [x] **Annotated mid-sentence:** open the screen RE-RUN (TASK-0386: replaced) and expect a dialog.

## 1.2 The overview ([[FEAT-0003]])
- [F] **Failed:** it broke.

# Tier 2 — Regression Tests

## 2.1 One vocabulary ([[ISS-0023]])
- [ ] **Regression:** the thing that broke stays fixed.

# Tier 3 — Verification Tests

## 3.1 This build
- [ ] **Build check:** only for this build.
"""


def _migrate(root: Path, *args: str) -> subprocess.CompletedProcess:
    import sys
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(root), *args],
        capture_output=True, text=True,
    )


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "tests").mkdir(parents=True)
    (tmp_path / "docs" / "tests" / "ACCEPTANCE_TESTS.md").write_text(
        SUITE, encoding="utf-8")
    (tmp_path / "SNAPSHOT.yaml").write_text(
        "counters:\n  CHK: 0\n", encoding="utf-8")
    return tmp_path


def _script():
    spec = importlib.util.spec_from_file_location("migrate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------ parity

def test_every_row_survives_with_its_verdict(repo: Path) -> None:
    """The claim the migration makes about itself, checked from outside it.

    Deliberately not *"the script printed parity OK"* — that is the script
    marking its own homework. This reads the file, migrates, reads the notes,
    and compares.
    """
    before = acceptance.parse(
        (repo / "docs" / acceptance.SUITE_REL).read_text(encoding="utf-8"))
    assert _migrate(repo, "--apply").returncode == 0

    after = acceptance.load_notes(repo / "docs" / acceptance.CHECKS_REL)
    assert len(after) == len(before) == 8
    for old, new in zip(before, after):
        assert new.name == old.name
        assert new.tier == old.tier and new.section == old.section
        assert new.area == old.area
        assert (new.checked, new.reconciled, new.excepted,
                new.failed, new.question) == (
            old.checked, old.reconciled, old.excepted, old.failed, old.question)
        assert new.settled is old.settled
        assert tuple(new.refs) == tuple(old.refs)


def test_the_gate_number_does_not_move(repo: Path) -> None:
    """The one number a release is decided by, before and after the cut."""
    docs = repo / "docs"
    before = acceptance.load(docs)
    assert before.shape == acceptance.SHAPE_FILE
    was_blocking = len(before.blocking())

    assert _migrate(repo, "--apply").returncode == 0
    after = acceptance.load(docs)
    assert after.shape == acceptance.SHAPE_NOTES
    assert len(after.blocking()) == was_blocking == 3


def test_legacy_marks_are_normalised_without_changing_a_verdict(repo: Path) -> None:
    """ADR-0029: `~` and `F` are read forever and never written.

    A migration writes every note in the corpus, so it is the one place that
    rule has teeth — and the normalisation must be a spelling change, never a
    verdict change, which is why the classification is asserted beside it.
    """
    assert _migrate(repo, "--apply").returncode == 0
    items = {i.name: i for i in
             acceptance.load_notes(repo / "docs" / acceptance.CHECKS_REL)}
    assert items["Reconciled"].mark == "/" and items["Reconciled"].reconciled
    assert items["Failed"].mark == "!" and items["Failed"].failed
    assert not any(i.mark in ("~", "F", "X") for i in items.values())


def test_the_annotation_becomes_a_field_wherever_it_sat(repo: Path) -> None:
    """`RE-RUN (…)` stops being prose — from both positions the fleet uses.

    28 of the fleet's 54 annotations end the line and 26 sit mid-sentence.
    Handling only the first would have left 26 checks with the annotation in
    their prose AND in their frontmatter, which is the dual source the whole
    decision exists to remove.
    """
    assert _migrate(repo, "--apply").returncode == 0
    items = {i.name: i for i in
             acceptance.load_notes(repo / "docs" / acceptance.CHECKS_REL)}
    tail = items["Annotated at the end"]
    assert tail.invalidated.change == "TASK-0385"
    assert tail.invalidated.reason == "the screen was replaced"
    assert "RE-RUN" not in tail.text

    middle = items["Annotated mid-sentence"]
    assert middle.invalidated.change == "TASK-0386"
    assert "RE-RUN" not in middle.text
    # The sentence still reads. A seam left as `screen  and expect` would be
    # the migration editing prose it was only supposed to move a span out of.
    assert middle.text == "open the screen and expect a dialog."


def test_a_ticked_row_with_an_invalidation_is_still_stale(repo: Path) -> None:
    """The measurement the whole phase turns on, preserved across the cut.

    54 of the fleet's annotated rows are ticked, which is why `your-trainer`'s
    honest blocking number is 113 rather than 60. **Not one of the 54 carries a
    date**, so a staleness rule keyed on date arithmetic alone would report
    zero stale rows the day the migration landed and read as an improvement.
    """
    assert _migrate(repo, "--apply").returncode == 0
    items = {i.name: i for i in
             acceptance.load_notes(repo / "docs" / acceptance.CHECKS_REL)}
    stale = items["Annotated at the end"]
    assert stale.checked and stale.invalidated and not stale.invalidated.date
    assert stale.stale is True


def test_prose_outside_the_tiers_moves_to_the_readme(repo: Path) -> None:
    """The preamble is not decoration — it holds the rules and every walk.

    A migration that moved the checkboxes and dropped the document's own
    account of what it is would lose more words than it moved.
    """
    assert _migrate(repo, "--apply").returncode == 0
    readme = (repo / "docs" / acceptance.CHECKS_REL / "README.md").read_text(
        encoding="utf-8")
    assert "New feature implemented -> add Tier 1 test(s)." in readme
    # The id survives, so `[[ACCEPTANCE-TESTS]]` still resolves somewhere.
    assert "id: ACCEPTANCE-TESTS" in readme
    assert "git show <ref>:docs/tests/ACCEPTANCE_TESTS.md" in readme
    # And no checkbox came with it — the checks are the notes now.
    assert "- [x] **Walked:" not in readme


def test_the_source_is_deleted_not_tombstoned(repo: Path) -> None:
    """Two copies of one record is the trap this project has paid for twice."""
    assert _migrate(repo, "--apply").returncode == 0
    assert not (repo / "docs" / acceptance.SUITE_REL).exists()


def test_a_dry_run_writes_nothing_and_still_reports_parity(repo: Path) -> None:
    """A dry run that cannot tell you whether it is safe is not worth having."""
    done = _migrate(repo)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "parity OK" in done.stdout
    assert (repo / "docs" / acceptance.SUITE_REL).exists()
    assert not (repo / "docs" / acceptance.CHECKS_REL).exists()


def test_it_refuses_to_run_twice(repo: Path) -> None:
    """The second run would allocate a second set of ids for the same checks."""
    assert _migrate(repo, "--apply").returncode == 0
    (repo / "docs" / acceptance.SUITE_REL).write_text(SUITE, encoding="utf-8")
    again = _migrate(repo, "--apply")
    assert again.returncode == 2 and "refusing to run twice" in again.stdout


def test_parity_failure_leaves_the_source_alone(repo: Path, monkeypatch) -> None:
    """The one failure mode with no recovery short of git, made unreachable.

    Driven by breaking the writer rather than by trusting the ordering of two
    statements: a migration that deletes first and checks second is one edit
    away at all times, and this is the assertion that would fail on that edit.
    """
    module = _script()
    original = module.note_text
    monkeypatch.setattr(
        module, "note_text",
        lambda item, **kw: original(item, **kw).replace('mark: "x"', 'mark: " "'))
    code = module.main.__wrapped__ if hasattr(module.main, "__wrapped__") else None
    assert code is None  # main() is plain; run it through argv instead
    import sys
    monkeypatch.setattr(sys, "argv",
                        ["migrate", "--repo-root", str(repo), "--apply"])
    assert module.main() == 1
    assert (repo / "docs" / acceptance.SUITE_REL).exists(), (
        "the source was deleted despite a parity failure")


# ------------------------------------------------- reading history at a ref

def test_the_delta_reads_both_shapes_at_their_own_refs(tmp_path: Path) -> None:
    """`suite_at` answers for a tag from before the cut and one from after.

    The two shapes are split by TIME, never maintained in parallel — so the
    guarantee worth asserting is that a tag cut before the migration still
    yields the numbers it always did, on the same code path, while a tag cut
    after yields them from notes.
    """
    root = tmp_path / "repo"
    (root / "docs" / "tests").mkdir(parents=True)
    (root / "SNAPSHOT.yaml").write_text("counters:\n  CHK: 0\n", encoding="utf-8")
    (root / "docs" / "tests" / "ACCEPTANCE_TESTS.md").write_text(
        SUITE, encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["add", "-A"],
                ["commit", "-qm", "the file shape"], ["tag", "v1"]):
        subprocess.run(["git", *cmd], cwd=root, check=True,
                       capture_output=True)

    assert _migrate(root, "--apply").returncode == 0
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "the note shape"], cwd=root,
                   check=True, capture_output=True)
    subprocess.run(["git", "tag", "v2"], cwd=root, check=True, capture_output=True)

    acceptance._at_ref.clear()
    before = acceptance.suite_at(root, "v1")
    after = acceptance.suite_at(root, "v2")
    assert before is not None and before.shape == acceptance.SHAPE_FILE
    assert after is not None and after.shape == acceptance.SHAPE_NOTES
    assert len(after.items) == len(before.items)
    assert len(after.blocking()) == len(before.blocking())
    # And the delta between them is empty, because nothing was WALKED — only
    # moved. A migration that showed up as five regressions would be telling
    # the reader that the storage change broke their release.
    split = acceptance.delta(after, before)
    assert split["comparable"] and not split["new"] and not split["regressed"]


def test_a_ref_with_no_suite_at_all_is_still_none(tmp_path: Path) -> None:
    """`None` and *"the suite had no items"* stay different answers.

    Absent is not passing — the sentence `acceptance.load` exists to protect,
    restated for the ref reader, which now has a second place to accidentally
    return an empty suite instead of nothing.
    """
    root = tmp_path / "bare"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "README.md").write_text("# nothing here\n", encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["add", "-A"],
                ["commit", "-qm", "no suite"], ["tag", "v1"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, capture_output=True)
    acceptance._at_ref.clear()
    assert acceptance.suite_at(root, "v1") is None


def test_the_note_shape_read_is_two_subprocesses_not_n(monkeypatch,
                                                       tmp_path: Path) -> None:
    """The cost claim in TASK-0462, asserted rather than asserted-about.

    `../your-trainer` has 579 checks and twelve tags. A per-file read would be
    6,948 subprocesses on a cold delta; the claim is that it is 24. Counted by
    intercepting the two call sites rather than by timing, because a timing
    assertion on a loaded machine is a flake with a moral.
    """
    root = tmp_path / "repo"
    (root / "docs" / "tests").mkdir(parents=True)
    (root / "SNAPSHOT.yaml").write_text("counters:\n  CHK: 0\n", encoding="utf-8")
    (root / "docs" / "tests" / "ACCEPTANCE_TESTS.md").write_text(
        SUITE, encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["add", "-A"],
                ["commit", "-qm", "file"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, capture_output=True)
    assert _migrate(root, "--apply").returncode == 0
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "notes"], cwd=root, check=True,
                   capture_output=True)
    subprocess.run(["git", "tag", "v2"], cwd=root, check=True, capture_output=True)

    # Counted at `subprocess.run`, the one place a process is actually
    # spawned. Counting at `_git_raw` as well double-counts the calls that go
    # through it, which is a guard reporting a cost that is not being paid.
    calls: list[str] = []
    real_run = subprocess.run

    def _counting(*args, **kwargs):
        argv = args[0] if args else kwargs.get("args") or []
        calls.append(" ".join(str(a) for a in argv[:4]))
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", _counting)

    acceptance._at_ref.clear()
    suite = acceptance.suite_at(root, "v2")
    assert suite is not None and len(suite.items) == 8
    # `git show` (misses), `git ls-tree`, `git cat-file` — three, whatever the
    # suite's size, and only the last two scale with anything.
    assert len(calls) == 3, calls


def test_the_ref_cache_holds(tmp_path: Path) -> None:
    """One read per (repo, ref) for the life of the process.

    A tag is immutable by convention, and the gate is on a page somebody clicks
    repeatedly — twelve tags re-read per render is the cost this cache exists
    to remove, and it must keep working now that a read is three subprocesses
    rather than one.
    """
    root = tmp_path / "repo"
    (root / "docs" / "tests").mkdir(parents=True)
    (root / "docs" / "tests" / "ACCEPTANCE_TESTS.md").write_text(
        SUITE, encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["add", "-A"],
                ["commit", "-qm", "file"], ["tag", "v1"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, capture_output=True)
    acceptance._at_ref.clear()
    first = acceptance.suite_at(root, "v1")
    shutil.rmtree(root / ".git")
    assert acceptance.suite_at(root, "v1") is first


def test_a_check_nobody_can_classify_blocks(tmp_path: Path) -> None:
    """The direction that fails safely, asserted rather than commented.

    A check whose `tier:` cannot be read is a check somebody wrote badly, not
    evidence that a release is clear. Dropping it and defaulting it to Tier 3
    are the SAME failure — both let a release through on a check nobody can
    read — and the first implementation did the first while its comment claimed
    the second was the danger. A mutation setting the fallback to Tier 3
    survived the whole suite, which is how the comment came to be checked.
    """
    checks = tmp_path / "docs" / acceptance.CHECKS_REL
    checks.mkdir(parents=True)
    (checks / "CHK-0001-Broken.md").write_text(
        "---\n"
        'type: "[[check]]"\nid: CHK-0001\ntitle: "Tier says nothing"\n'
        'status: active\ntier: ""\narea: "x"\nsection: "1.1"\nordinal: 10\n'
        'mark: "x"\n---\n\n# Tier says nothing\n\nDo it.\n',
        encoding="utf-8")
    items = acceptance.load_notes(checks)
    assert len(items) == 1, "the check vanished from the suite"
    assert items[0].tier == 1, "an unclassifiable check must gate a release"
    suite = acceptance.Suite(items=items, shape=acceptance.SHAPE_NOTES)
    # …and it does block, even carrying `x`: a mark on a check whose tier is
    # unreadable is a claim about something nobody can place.
    assert len(suite.tier(1)) == 1


def test_a_note_with_no_id_is_not_a_check(tmp_path: Path) -> None:
    """The one case that IS dropped, and the reason it is different: a note
    with no id is not a malformed check, it is not a check."""
    checks = tmp_path / "docs" / acceptance.CHECKS_REL
    checks.mkdir(parents=True)
    (checks / "CHK-README.md").write_text(
        '---\ntype: "[[reference]]"\ntitle: "Not a check"\n---\n\n# Prose\n',
        encoding="utf-8")
    assert acceptance.load_notes(checks) == []


def test_a_ref_read_survives_non_ascii_prose(tmp_path: Path) -> None:
    """`git cat-file --batch` sizes are BYTES; the walk must not count characters.

    This is the defect that shipped and was caught by measurement rather than
    by reading: on `../your-trainer` the note-shape read returned **314 of 579**
    checks with no error, because 503,860 bytes of notes decode to 501,153
    characters and the walk drifted one position per non-ASCII byte until it
    hit a header it could not parse. The gate at every post-migration ref would
    have read 20 blocking where the truth is 60 — the direction that lets a
    release through.

    The fixture puts the multi-byte characters in the FIRST note deliberately.
    Drift only affects what comes after it, so a corpus whose non-ASCII sits in
    the last note round-trips perfectly and proves nothing.
    """
    root = tmp_path / "repo"
    checks = root / "docs" / acceptance.CHECKS_REL
    checks.mkdir(parents=True)
    for n in range(1, 7):
        # Em-dash, tick and arrow — all three appear in the real corpus, and
        # all three are multi-byte in UTF-8.
        prose = ("walked — expect ✅ and the row → moves" if n == 1
                 else "plain ascii prose")
        (checks / f"CHK-{n:04d}-Row.md").write_text(
            "---\n"
            f'type: "[[check]]"\nid: CHK-{n:04d}\ntitle: "Row {n}"\n'
            'status: active\ntier: 1\narea: "A"\nsection: "1.1"\n'
            f"ordinal: {n * 10}\n"
            'mark: " "\ninvalidated_by: {}\ncovers: []\n---\n\n'
            f"# Row {n}\n\n{prose}\n", encoding="utf-8")
    for cmd in (["init", "-q"], ["config", "user.email", "t@example.com"],
                ["config", "user.name", "T"], ["add", "-A"],
                ["commit", "-qm", "notes"], ["tag", "v1"]):
        subprocess.run(["git", *cmd], cwd=root, check=True, capture_output=True)

    acceptance._at_ref.clear()
    suite = acceptance.suite_at(root, "v1")
    assert suite is not None
    assert [i.note_id for i in suite.items] == [f"CHK-{n:04d}" for n in range(1, 7)], (
        "the ref read lost notes after the one carrying multi-byte characters"
    )
    # The prose survives intact, not merely the count — a slice that is short
    # by two bytes still yields a parseable note with a truncated body.
    assert suite.items[0].text == "walked — expect ✅ and the row → moves"
    # …and every one of them still blocks, which is what the gate reads.
    assert len(suite.blocking()) == 6
