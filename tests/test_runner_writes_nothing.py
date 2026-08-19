"""`run-tests.py` reports and does not write ([[REQ-0058]], TASK-0559).

A test note carrying a `command:` records that a machine executes it. Whether the
machine was happy is CI's answer, and CI answers it better: a stamped `passing`
cannot notice that the test it stands for was renamed, and a `command:` that
stops resolving can.

The guard is **byte-identity of the note**, not "status is unchanged". Stamping
also wrote `last_run:`, `exit_code:` and `updated:`, and a test keyed on `status`
alone would pass while three other fields were still being rewritten -- which is
exactly the state `your-trainer` is in today: 69 orphan `exit_code` values
against 2 verdicts.

The mutant this must fail on is the one that matters: restore any single
frontmatter write and `test_a_failing_command_leaves_the_note_alone` breaks,
because a failing outcome is the one that used to write hardest.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "tools" / "scripts" / "run-tests.py"

NOTE = """---
type: "[[test]]"
id: TST-0001
title: "A note that used to be stamped"
status: active
command: {command}
last_run: ""
exit_code: ""
updated: 2026-01-01
---

# Body
"""


def _runner():
    spec = importlib.util.spec_from_file_location("run_tests_nw", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def repo(tmp_path: Path):
    (tmp_path / "SNAPSHOT.yaml").write_text("counters:\n  TST: 1\n", encoding="utf-8")
    (tmp_path / "docs" / "tests").mkdir(parents=True)
    return tmp_path


def _note(repo: Path, command: str) -> Path:
    p = repo / "docs" / "tests" / "TST-0001-Stamped.md"
    p.write_text(NOTE.format(command=command), encoding="utf-8")
    return p


def _execute(repo: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo), *args],
        capture_output=True, text=True, timeout=120,
    )


# ------------------------------------------------------------------ the rule

@pytest.mark.parametrize("command,label", [
    ("\"exit 0\"", "passing"),
    ("\"exit 1\"", "failing"),
    ("\"no-such-binary-xyz\"", "unrunnable"),
])
def test_no_outcome_writes_anything(repo: Path, command: str, label: str) -> None:
    """All three outcomes, including the two that used to write."""
    note = _note(repo, command)
    before = note.read_bytes()
    result = _execute(repo, "--write")
    assert label in result.stdout, result.stdout
    assert note.read_bytes() == before, "the note was rewritten"


def test_a_failing_command_leaves_the_note_alone(repo: Path) -> None:
    """The outcome that used to write hardest -- and destroyed a verdict doing it.

    ISS-0239: a missing device exited non-zero, landed in `failing`, and flipped
    `TST-0017` from `passing` with a newer `last_run`. Under this rule there is
    no verdict in the note for a non-result to destroy.
    """
    note = _note(repo, "\"exit 1\"")
    before = note.read_text(encoding="utf-8")
    assert _execute(repo, "--write").returncode == 1, "a failure is still reported"
    assert note.read_text(encoding="utf-8") == before


def test_write_is_accepted_and_says_it_does_nothing(repo: Path) -> None:
    """Kept and inert: `--write` must not become an unknown-option error.

    Every existing invocation passes it. "There is nothing to write" is a
    different answer from "no such flag", and only one of them is true.
    """
    _note(repo, "\"exit 0\"")
    result = _execute(repo, "--write")
    assert result.returncode == 0
    assert "ignored" in result.stderr.lower()


def test_the_script_carries_no_way_to_write_frontmatter(repo: Path) -> None:
    """Structural, not behavioural: the helper is gone, not merely unused.

    A dead `fm_set` sitting in a script that must not write is one edit away
    from writing again, and no behavioural test would notice it come back.
    """
    module = _runner()
    assert not hasattr(module, "fm_set")
    assert "write_text" not in SCRIPT.read_text(encoding="utf-8")
