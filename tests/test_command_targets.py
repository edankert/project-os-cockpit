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
