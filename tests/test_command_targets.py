"""A `command:` that stops resolving is the one thing an automated test owes.

**This cannot be proved from the corpus, and saying so is half the test.**
Measured 2026-08-19 across all 139 automated notes in the fleet: 134 resolve, 5
name nothing checkable, and **zero are broken**. A test written over that data
passes whether or not the code works -- the trap TASK-0556's child sort fell
into, where a corpus assertion agreed with any implementation and the mutant
survived it.

So every case here is constructed: a repo is built, a covering test is deleted,
and the check is asserted to notice. `test_the_mutant_is_caught` is the one that
proves the rest are load-bearing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from project_os_cockpit import command_targets as ct


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_present.py").write_text("def test_x(): pass\n", encoding="utf-8")
    src = tmp_path / "android" / "app" / "src" / "test" / "kotlin" / "com" / "x"
    src.mkdir(parents=True)
    (src / "PresentTest.kt").write_text("class PresentTest\n", encoding="utf-8")
    return tmp_path


# --------------------------------------------------------------- resolves

@pytest.mark.parametrize("command", [
    "pytest tests/test_present.py -q",
    "pytest tests/test_present.py::test_x -q",
    "cd android && ./gradlew :app:testDebugUnitTest --tests com.x.PresentTest",
    "./gradlew :app:connectedDebugAndroidTest "
    "-Pandroid.testInstrumentationRunnerArguments.class=com.x.PresentTest",
])
def test_a_command_naming_something_present_resolves(repo: Path, command: str) -> None:
    assert ct.resolve(command, repo) == ct.RESOLVES


# ----------------------------------------------------------------- broken

def test_a_deleted_covering_test_breaks_the_command(repo: Path) -> None:
    """The whole point, and the case the corpus cannot supply.

    This is FEAT-0138's acceptance criterion 4 in miniature: delete the test
    that covers a check, and the check must come back on its own.
    """
    command = "pytest tests/test_present.py -q"
    assert ct.resolve(command, repo) == ct.RESOLVES
    (repo / "tests" / "test_present.py").unlink()
    assert ct.resolve(command, repo) == ct.BROKEN


def test_a_renamed_jvm_class_breaks_the_command(repo: Path) -> None:
    """A rename is the case a stamped `passing` structurally cannot notice."""
    command = "cd android && ./gradlew :app:testDebugUnitTest --tests com.x.PresentTest"
    assert ct.resolve(command, repo) == ct.RESOLVES
    src = repo / "android/app/src/test/kotlin/com/x"
    (src / "PresentTest.kt").rename(src / "RenamedTest.kt")
    assert ct.resolve(command, repo) == ct.BROKEN


def test_one_missing_target_among_several_is_broken(repo: Path) -> None:
    """Fail closed: a command is only whole if every target it names exists."""
    assert ct.resolve(
        "pytest tests/test_present.py tests/test_absent.py -q", repo) == ct.BROKEN


# ------------------------------------------------------------ uncheckable

@pytest.mark.parametrize("command", [
    "make check",
    "bash tools/scripts/validate-docs.sh --quiet",
    "./gradlew test --rerun-tasks",
])
def test_a_command_naming_no_target_is_uncheckable(repo: Path, command: str) -> None:
    """**A third answer, on purpose.**

    Five of the fleet's 139 automated notes are this. Calling them `resolves`
    asserts coverage nobody verified; calling them `broken` puts five working
    checks on a list of things to fix.
    """
    assert ct.resolve(command, repo) == ct.UNCHECKABLE


def test_only_a_checkable_missing_target_is_broken(repo: Path) -> None:
    assert ct.is_broken("make check", repo) is False
    assert ct.is_broken("pytest tests/test_absent.py", repo) is True


def test_an_unbalanced_quote_is_not_a_broken_test(repo: Path) -> None:
    """A command this cannot parse is a command this cannot check."""
    assert ct.resolve('pytest "tests/test_present.py -q', repo) == ct.UNCHECKABLE


# ------------------------------------------------------------- the mutant

def test_the_mutant_is_caught(repo: Path) -> None:
    """If `_exists` always said yes, would anything above fail?

    Asserted directly rather than trusted, because the corpus holds no broken
    command and every other assertion here would survive that mutation if the
    constructed cases were wrong.
    """
    real = ct._exists
    try:
        ct._exists = lambda kind, value, root: True          # the mutant
        assert ct.resolve("pytest tests/test_absent.py", repo) == ct.RESOLVES, (
            "the mutant did not change behaviour — these tests prove nothing")
    finally:
        ct._exists = real
    assert ct.resolve("pytest tests/test_absent.py", repo) == ct.BROKEN


# ------------------------------------------- the navigator (independent review)

def _corpus(root: Path, *, command: str) -> Path:
    """A repo with one automated test and the source its command names."""
    docs = root / "docs" / "tests"
    docs.mkdir(parents=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / "present.py").write_text("x = 1\n", encoding="utf-8")
    (root / "SNAPSHOT.yaml").write_text(
        "version: 1\ncounters:\n  TST: 2\nitems: {}\n", encoding="utf-8")
    (docs / "TST-0002-Automated.md").write_text(
        '---\ntype: "[[test]]"\nid: TST-0002\ntitle: "an automated test"\n'
        f'status: active\ncovers: ["[[FEAT-0001]]"]\ncommand: "{command}"\n'
        "---\n\n# body\n", encoding="utf-8")
    return root / "docs"


def _sections(docs: Path) -> dict[str, list[str]]:
    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    out: dict[str, list[str]] = {}
    for group in cockpit._tests_groups(Index.build(docs)):
        out[str(group["key"])] = [str(i.get("id")) for i in group["items"]]
    return out


def test_a_broken_command_routes_to_its_own_section(tmp_path: Path) -> None:
    """**The resolver returning BROKEN is not the same as the reader acting on it.**

    Independent review, 2026-08-20: replacing the `broken-command` branch in
    `_tests_groups` with an unconditional `automated` append — deleting the
    section outright — passed all 1854 tests. Every guard was on
    `command_targets` in isolation, and nothing asserted the navigator routed
    anything, so the exit criterion *"deleting a covering test puts its check
    back on the list"* proved a function returned a string.

    This is the criterion, end to end: a check whose covering test is deleted
    leaves `Automated tests` and lands somewhere a person is asked to look.
    """
    docs = _corpus(tmp_path, command="pytest tests/present.py")
    assert _sections(docs).get("automated") == ["TST-0002"]

    (tmp_path / "tests" / "present.py").unlink()
    sections = _sections(docs)
    assert sections.get("broken-command") == ["TST-0002"]
    assert "TST-0002" not in sections.get("automated", [])


def test_the_broken_section_asks_for_a_person(tmp_path: Path) -> None:
    """It is an obligation, not a category — the only one an automated test
    can carry, and the reason it exists at all."""
    from project_os_cockpit import cockpit
    from project_os_cockpit.index import Index

    docs = _corpus(tmp_path, command="pytest tests/absent.py")
    groups = {g["key"]: g for g in cockpit._tests_groups(Index.build(docs))}
    assert groups["broken-command"].get("needs_human") is True
    assert "automated" not in groups or not groups["automated"]["items"]


def test_an_uncheckable_command_stays_automated(tmp_path: Path) -> None:
    """Five of the fleet's 139 name nothing checkable. They are not broken,
    and putting them on a list of things to fix would be a lie about five
    working checks."""
    docs = _corpus(tmp_path, command="make check")
    sections = _sections(docs)
    assert sections.get("automated") == ["TST-0002"]
    assert "broken-command" not in sections
