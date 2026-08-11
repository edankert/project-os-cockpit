"""The shape of a change, keyed to a note (ISS-0096).

History answers *what moved* — status transitions grouped by commit, which
FEAT-0052 measured as the honest signal. It cannot answer **what was touched**,
because `commits_payload` discards every non-`.md` path on purpose, for its own
question.

At acceptance time the reader is asking *did this touch what it claims to* — a
task promising a CSS fix that rewrote the validator is one line of shape and
invisible in prose.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import cockpit

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    (root / "docs").mkdir(parents=True)
    (root / "src").mkdir()
    (root / "tests").mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)

    (root / "docs" / "note.md").write_text("# n\n", encoding="utf-8")
    (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    (root / "tests" / "test_thing.py").write_text("def test_x(): pass\n", encoding="utf-8")
    (root / "style.css").write_text("body{}\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "TASK-9001: touch four kinds"], cwd=root, check=True)

    (root / "docs" / "other.md").write_text("# o\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "TASK-9002: unrelated"], cwd=root, check=True)
    return root


def test_the_shape_groups_by_kind_not_by_directory(repo: Path) -> None:
    """The buckets answer "did this touch what it claims to", so a CSS file and
    a source file must not collapse into one number."""
    shape = cockpit.change_shape_payload(repo, "TASK-9001")
    assert shape["available"] is True
    assert shape["files"] == 4, shape
    assert shape["kinds"]["notes"] == 1
    assert shape["kinds"]["source"] == 1
    assert shape["kinds"]["tests"] == 1
    assert shape["kinds"]["assets"] == 1, shape["kinds"]


def test_only_the_notes_commits_are_counted(repo: Path) -> None:
    """Keyed to the note: an unrelated commit must not inflate the shape."""
    shape = cockpit.change_shape_payload(repo, "TASK-9001")
    assert len(shape["commits"]) == 1
    assert "TASK-9001" in shape["commits"][0]["subject"]


def test_a_note_git_never_saw_reports_nothing_rather_than_erroring(repo: Path) -> None:
    """Absent, not zero — a `Changed · 0` card on every unbuilt note is the
    permanent zero this surface has been taught about twice."""
    shape = cockpit.change_shape_payload(repo, "TASK-9999")
    assert shape["available"] is True
    assert shape["files"] == 0 and shape["commits"] == []


def test_a_directory_that_is_not_a_repo_is_unavailable(tmp_path: Path) -> None:
    shape = cockpit.change_shape_payload(tmp_path, "TASK-9001")
    assert shape["available"] is False


def test_an_empty_id_does_not_match_every_commit(repo: Path) -> None:
    """`--grep=` with an empty pattern matches everything; the shape of "no
    note" would then be the shape of the whole repository."""
    shape = cockpit.change_shape_payload(repo, "")
    assert shape["available"] is False
    assert shape["files"] == 0


def test_it_answers_for_this_repos_own_work() -> None:
    """Against the real corpus, because the fixture cannot exercise scale."""
    shape = cockpit.change_shape_payload(REPO, "ISS-0135")
    assert shape["available"] is True
    assert shape["files"] > 0
    # The point of the issue: non-note files survive, where commits_payload
    # drops them.
    assert set(shape["kinds"]) - {"notes"}, (
        "only notes were counted — this is what commits_payload already did"
    )
