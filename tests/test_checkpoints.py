"""Per-turn checkpoints (FEAT-0078 / TASK-0335).

RISK-0006's first hazard is compounding judgment: a wrong assumption at hour
one is the context of every decision after it. The only unit of undo today is
the close-out commit — the whole session, or nothing.

Three properties carry the safety, and each is a way this could be worse than
useless:

* **outside every push path** — a checkpoint is taken automatically dozens of
  times an hour, and publishing is a deliberate act;
* **untracked files included** — an agent's damage is often a file it *added*;
* **the real index untouched** — a safety net that rewrites your staging area
  is a second actor, not a net.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import checkpoints


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
    (root / "tracked.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
    return root


def _refs(root: Path, pattern: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "for-each-ref", "--format=%(refname)", pattern],
        capture_output=True, text=True, check=False,
    )
    return [ln for ln in out.stdout.splitlines() if ln]


def test_a_checkpoint_lands_outside_heads_and_tags(repo: Path) -> None:
    """A hundred turn refs in `git branch` is a tool nobody keeps — and a ref
    under `refs/heads` is pushed by default."""
    result = checkpoints.capture(repo, label="turn 1")
    assert result["ok"] is True, result
    assert result["ref"].startswith("refs/cockpit/turns/")
    assert _refs(repo, "refs/heads") == ["refs/heads/main"] or _refs(repo, "refs/heads") == ["refs/heads/master"]
    assert not _refs(repo, "refs/tags")


def test_untracked_files_are_captured(repo: Path) -> None:
    """An agent's damage is often a file it ADDED; a checkpoint that captured
    only tracked changes would restore a tree still carrying it."""
    (repo / "added-by-agent.txt").write_text("oops\n", encoding="utf-8")
    result = checkpoints.capture(repo, label="turn with an untracked file")
    listed = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", result["sha"]],
        capture_output=True, text=True, check=False,
    ).stdout.split()
    assert "added-by-agent.txt" in listed, listed


def test_the_real_index_is_untouched(repo: Path) -> None:
    """A safety net that rewrites your staging area is a second actor."""
    (repo / "staged.txt").write_text("s\n", encoding="utf-8")
    subprocess.run(["git", "add", "staged.txt"], cwd=repo, check=True)
    (repo / "unstaged.txt").write_text("u\n", encoding="utf-8")

    before = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    ).stdout.split()
    checkpoints.capture(repo, label="mid-add")
    after = subprocess.run(
        ["git", "-C", str(repo), "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    ).stdout.split()
    assert before == after == ["staged.txt"], (before, after)


def test_checkpoints_list_newest_first(repo: Path) -> None:
    for n in range(3):
        (repo / "tracked.txt").write_text(f"{n}\n", encoding="utf-8")
        checkpoints.capture(repo, label=f"turn {n}")
    rows = checkpoints.listing(repo)
    assert len(rows) == 3
    assert "turn 2" in rows[0]["subject"], rows[0]


def test_pruning_keeps_the_newest(repo: Path) -> None:
    """Stated where it is set: a day of hard use is a few hundred turns."""
    for n in range(5):
        (repo / "tracked.txt").write_text(f"{n}\n", encoding="utf-8")
        checkpoints.capture(repo, label=f"turn {n}")
    dropped = checkpoints.prune(repo, keep=2)
    rows = checkpoints.listing(repo)
    assert dropped == 3 and len(rows) == 2
    assert "turn 4" in rows[0]["subject"]


def test_a_non_repo_reports_rather_than_raising(tmp_path: Path) -> None:
    assert checkpoints.available(tmp_path) is False
    assert checkpoints.capture(tmp_path)["ok"] is False
    assert checkpoints.listing(tmp_path) == []


def test_the_namespace_is_stated_once() -> None:
    """One constant, so excluding it from a push path is a lookup rather than
    a remembered string."""
    src = (
        Path(__file__).resolve().parent.parent
        / "src" / "project_os_cockpit" / "checkpoints.py"
    ).read_text(encoding="utf-8")
    assert src.count('REF_NAMESPACE = "refs/cockpit/turns"') == 1
    assert "refs/heads" not in src.split("REF_NAMESPACE =")[1].split("\n")[0]
