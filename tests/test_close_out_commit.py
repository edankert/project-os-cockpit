"""close-out-commit.sh (FEAT-0055 / TASK-0264).

The script commits what a close-out just finished. Its whole reason for
existing is what it does **not** do:

- it never runs `git add -A`, because on 2026-07-30 `your-trainer`
  carried 44 uncommitted files and `your-health` 8, none of them the work
  in hand and all deliberately untouched;
- it refuses with no paths, which is `-A` wearing a different name;
- it never passes `--no-verify`, because the pre-commit hook is the gate.

Exercised against real throwaway repositories: the behaviour under test
is git's, and a mocked git would only prove the mock.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "scripts" / "close-out-commit.sh"


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=str(repo), capture_output=True, text=True, timeout=60,
    )


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    ).stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway repo with one commit and no hooks."""
    r = tmp_path / "r"
    (r / "docs").mkdir(parents=True)
    (r / "src").mkdir()
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    for k, v in (("user.email", "t@e.st"), ("user.name", "T")):
        subprocess.run(["git", "-C", str(r), "config", k, v], check=True)
    (r / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(r), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(r), "commit", "-qm", "seed"], check=True)
    return r


def test_it_refuses_with_no_paths(repo: Path) -> None:
    """`add -A` wearing a different name."""
    res = _run(repo)
    assert res.returncode == 2
    assert "no paths given" in res.stderr


def test_it_stages_only_what_it_was_given(repo: Path) -> None:
    """The rule the whole script exists for.

    A dirty file outside the close-out's scope is somebody else's work in
    progress. It must survive untouched.
    """
    # Covers: TST-0069 — "named paths staged"
    (repo / "docs" / "ISS-0001-Thing.md").write_text("---\nid: ISS-0001\n---\n", encoding="utf-8")
    (repo / "src" / "unrelated.py").write_text("# someone else's afternoon\n", encoding="utf-8")

    res = _run(repo, "docs")
    assert res.returncode == 0, res.stderr

    committed = _git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert "docs/ISS-0001-Thing.md" in committed
    assert "src/unrelated.py" not in committed, (
        "the script committed a file outside the paths it was given"
    )
    # …and it is still there, dirty, for its owner. `-uall` because the
    # default collapses untracked content to the directory — the same
    # granularity trap the script itself had to avoid.
    assert "src/unrelated.py" in _git(repo, "status", "--porcelain", "-uall")


def test_it_reports_what_it_left_alone(repo: Path) -> None:
    """Silence would look identical to having committed it."""
    # Covers: TST-0069 — "dirty files elsewhere reported and left alone"
    (repo / "docs" / "a.md").write_text("a\n", encoding="utf-8")
    (repo / "src" / "b.py").write_text("b\n", encoding="utf-8")
    res = _run(repo, "docs")
    assert "src/b.py" in res.stderr, "the out-of-scope file was not reported"
    assert "src/b.py" in _git(repo, "log", "-1", "--format=%b"), (
        "the commit body should record what was deliberately excluded"
    )


def test_the_message_names_the_ids_that_closed(repo: Path) -> None:
    # Covers: TST-0069 — "the message built from the staged ids"
    (repo / "docs" / "FEAT-0042-Thing.md").write_text("x\n", encoding="utf-8")
    (repo / "docs" / "TASK-0100-Bit.md").write_text("y\n", encoding="utf-8")
    _run(repo, "docs")
    subject = _git(repo, "log", "-1", "--format=%s")
    assert "FEAT-0042" in subject and "TASK-0100" in subject, subject


def test_extra_context_reaches_the_subject(repo: Path) -> None:
    (repo / "docs" / "ISS-0002-X.md").write_text("x\n", encoding="utf-8")
    _run(repo, "docs", "-m", "the reason")
    assert "the reason" in _git(repo, "log", "-1", "--format=%s")


def test_it_does_not_push(repo: Path, tmp_path: Path) -> None:
    """A commit is local and reversible; a push is publishing."""
    # Covers: TST-0069 — "and no push"
    bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(bare)], check=True)
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    subprocess.run(["git", "-C", str(repo), "push", "-q", "-u", "origin", branch], check=True)

    (repo / "docs" / "c.md").write_text("c\n", encoding="utf-8")
    _run(repo, "docs")
    assert _git(repo, "rev-list", "--count", "@{u}..HEAD") == "1", (
        "the script pushed — it must only ever commit"
    )


def test_it_refuses_mid_merge(repo: Path) -> None:
    (repo / ".git" / "MERGE_HEAD").write_text("deadbeef\n", encoding="utf-8")
    res = _run(repo, "docs")
    assert res.returncode == 2
    assert "merge is in progress" in res.stderr


def test_it_never_bypasses_the_hook() -> None:
    """The pre-commit hook syncs the snapshot and runs the validator.

    `--no-verify` would make the commit succeed where the validator says
    it should not — the exact bypass the hook's own comment records
    agents having done.
    """
    # Covers: TST-0069 — "the pre-commit hook run"
    # Assert on the INVOCATION, not on a mention: the script's header
    # explains why the flag is absent, and a substring check would flag
    # that explanation — the false-positive shape ISS-0069 recorded.
    import re
    src = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"git commit[^\n]*--no-verify", src), (
        "the script bypasses the pre-commit hook"
    )


def test_add_dash_A_appears_nowhere() -> None:
    """The single most important line that must not exist."""
    import re
    src = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"git add\s+(-A|--all|\.)\s*$", src, re.M), (
        "the script stages everything — see your-trainer's 44 dirty files"
    )
