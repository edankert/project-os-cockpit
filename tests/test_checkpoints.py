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


# ---------------------------------------------------------------------------
# TASK-0336 — the turn timeline
# ---------------------------------------------------------------------------


def test_turns_are_newest_first_even_within_one_second(repo: Path) -> None:
    """The bug this caught, kept as the guard.

    Git's `creatordate` has SECOND granularity, so two checkpoints in the same
    second tie — and the first rendering of this timeline came out **reversed**,
    attributing each turn's changes to its neighbour. For a "where did it go
    wrong" slider, out-of-order turns are worse than no turns.
    """
    for n in range(4):
        (repo / f"file{n}.py").write_text(f"x = {n}\n", encoding="utf-8")
        checkpoints.capture(repo, label=f"turn {n}")
    rows = checkpoints.turns(repo)
    labels = [r["subject"] for r in rows]
    assert labels == sorted(labels, reverse=True), labels
    assert "turn 3" in labels[0], labels


def test_a_turn_reports_what_changed_since_the_one_before(repo: Path) -> None:
    checkpoints.capture(repo, label="turn 1")
    (repo / "style.css").write_text("body{}\n", encoding="utf-8")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "note.md").write_text("# n\n", encoding="utf-8")
    checkpoints.capture(repo, label="turn 2")

    newest = checkpoints.turns(repo)[0]
    assert newest["files"] == 2, newest
    assert newest["kinds"] == {"assets": 1, "notes": 1}, newest["kinds"]


def test_the_first_turn_says_so_rather_than_reporting_nothing(repo: Path) -> None:
    """`0 files` on the earliest checkpoint would read as "this turn did
    nothing" rather than "we started measuring here"."""
    checkpoints.capture(repo, label="only turn")
    oldest = checkpoints.turns(repo)[-1]
    assert oldest["from_start"] is True


def test_the_timeline_shares_the_shape_function_it_does_not_copy_it() -> None:
    """"Which files, grouped by kind" is one question with one answer.

    Computing it a second way here is how the two would come to disagree about
    what counts as a test — ISS-0023's failure, in a new place.
    """
    src = (
        Path(__file__).resolve().parent.parent
        / "src" / "project_os_cockpit" / "checkpoints.py"
    ).read_text(encoding="utf-8")
    assert "from .cockpit import _shape_kind" in src
    assert "tests/" not in src, "the kind buckets are restated here instead of imported"


# ---------------------------------------------------------------------------
# TASK-0337 — restore, which is principal-owned
# ---------------------------------------------------------------------------


def test_a_worker_may_never_rewind_itself(repo: Path) -> None:
    """ADR-0009 puts rewind with the principal, and the reason is not ceremony:
    a loop that can undo its own turns can erase the evidence of having gone
    wrong — which is the one thing checkpoints exist to preserve."""
    cp = checkpoints.capture(repo, label="good")
    for who in ("agent", "worker", "agent:worker", "agent:something"):
        got = checkpoints.restore(repo, cp["sha"], actor=who)
        assert got["ok"] is False, f"{who} was allowed to restore"
        assert "principal-owned" in got["error"]


def test_restore_without_an_actor_is_refused(repo: Path) -> None:
    """An unattributed rewind is indistinguishable from a worker's."""
    cp = checkpoints.capture(repo, label="good")
    assert checkpoints.restore(repo, cp["sha"], actor="")["ok"] is False


def test_a_restore_captures_the_state_it_replaces_first(repo: Path) -> None:
    """A restore is never the end of a road.

    Without this, `restore` is a destructive verb wearing a safe name: the
    state being rewound away would be gone.
    """
    (repo / "tracked.txt").write_text("good\n", encoding="utf-8")
    cp = checkpoints.capture(repo, label="good state")
    (repo / "tracked.txt").write_text("damaged\n", encoding="utf-8")

    got = checkpoints.restore(repo, cp["sha"], actor="user:edwin")
    assert got["ok"] is True, got
    assert (repo / "tracked.txt").read_text(encoding="utf-8") == "good\n"

    # The damaged state is still reachable.
    safety = got["safety_checkpoint"]
    blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"{safety}:tracked.txt"],
        capture_output=True, text=True, check=False,
    ).stdout
    assert blob == "damaged\n", "the state being replaced was lost"


def test_restoring_an_unknown_checkpoint_changes_nothing(repo: Path) -> None:
    (repo / "tracked.txt").write_text("intact\n", encoding="utf-8")
    got = checkpoints.restore(repo, "0" * 40, actor="user:edwin")
    assert got["ok"] is False
    assert (repo / "tracked.txt").read_text(encoding="utf-8") == "intact\n"


def test_the_principal_identity_is_allowed(repo: Path) -> None:
    """`agent:principal` is the delegated principal (ADR-0009), not a worker —
    the distinction the whole delegation model rests on."""
    cp = checkpoints.capture(repo, label="good")
    assert checkpoints.restore(repo, cp["sha"], actor="agent:principal")["ok"] is True
