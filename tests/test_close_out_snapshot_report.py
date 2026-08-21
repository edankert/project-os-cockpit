"""`close-out-commit.sh` names what it changes in `SNAPSHOT.yaml` ([[ISS-0252]]).

**Three collisions in one afternoon**, closing out [[PHASE-037]] alongside a
second session. Every close-out must name `SNAPSHOT.yaml` — `sync-snapshot.py`
writes counters and metrics into it at pre-commit and the validator errors if
they are stale — so every session commits the same hand-curated shared file.

The collision that matters is the second: a commit swept in the other session's
hand-written `PHASE-040:` entry while the note was still untracked, turning
`--as-committed` red with `ITEM-FILE`. **It does not self-heal** — a dangling
reference stays dangling — and the local validator cannot see it, because it
reads the working tree, where the note exists.

*"Collision 2 was visible in `git diff` and nobody looked."* So it is printed.

**The collision is constructed here and the report is watched firing**, which
is [[ISS-0252]]'s fourth Next Action.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "scripts" / "close-out-commit.sh"

ENV = {
    "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@e",
    "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@e",
    "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
    "HOME": "/tmp",
}

SNAPSHOT = """version: 1
updated: "2026-08-21"
counters:
  FEAT: 1
focus:
  task: ""
items:
  features:
    FEAT-0001:
      file: "docs/features/f/FEAT-0001-F.md"
      status: done
"""

NOTE = ('---\ntype: "[[feature]]"\nid: FEAT-0001\ntitle: "F"\n'
        "status: done\n---\n\n# F\n")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, env=ENV,
                          capture_output=True, text=True)


def _repo(tmp: Path) -> Path:
    repo = tmp / "r"
    (repo / "docs" / "features" / "f").mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "main", str(repo))
    (repo / "SNAPSHOT.yaml").write_text(SNAPSHOT, encoding="utf-8")
    (repo / "docs" / "features" / "f" / "FEAT-0001-F.md").write_text(
        NOTE, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo


def _run(repo: Path, *paths: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), *paths], cwd=repo, env=ENV,
                          capture_output=True, text=True)


def _register(repo: Path, item: str, rel: str) -> None:
    """The other session's hand edit: an `items:` entry appears in the shared
    file. Membership is curation `sync-snapshot.py` deliberately leaves alone,
    so it sits there until *somebody* commits it."""
    text = (repo / "SNAPSHOT.yaml").read_text(encoding="utf-8")
    (repo / "SNAPSHOT.yaml").write_text(
        text + f'  phases:\n    {item}:\n      file: "{rel}"\n'
               f'      status: active\n', encoding="utf-8")


# ---- the collision, constructed ------------------------------------------

def test_an_entry_whose_note_is_in_no_commit_is_named_as_dangling(
        tmp_path: Path) -> None:
    """Collision 2, exactly: the entry is committed, the note is not, and the
    reference dangles from that moment on."""
    repo = _repo(tmp_path)
    rel = "docs/phases/PHASE-0040-P.md"
    (repo / "docs" / "phases").mkdir(parents=True)
    #: The note exists ON DISK — which is why the local validator passes.
    (repo / rel).write_text(
        '---\ntype: "[[phase]]"\nid: PHASE-0040\ntitle: "P"\nstatus: active\n'
        'order: 40\n---\n\n# P\n', encoding="utf-8")
    _register(repo, "PHASE-0040", rel)

    out = _run(repo, "SNAPSHOT.yaml")
    assert out.returncode == 0, out.stderr
    assert "PHASE-0040" in out.stderr, out.stderr
    assert "DANGLING" in out.stderr, out.stderr
    #: And it is in the commit message, so `git log` carries it too.
    log = _git(repo, "log", "-1", "--format=%B").stdout
    assert "membership changed" in log and "PHASE-0040" in log


def test_an_entry_committed_with_its_note_is_listed_but_not_dangling(
        tmp_path: Path) -> None:
    """The ordinary close-out: the session registering an item is the session
    committing its note. Reported — membership changed and that is worth
    seeing — but nothing is broken."""
    repo = _repo(tmp_path)
    rel = "docs/phases/PHASE-0040-P.md"
    (repo / "docs" / "phases").mkdir(parents=True)
    (repo / rel).write_text(
        '---\ntype: "[[phase]]"\nid: PHASE-0040\ntitle: "P"\nstatus: active\n'
        'order: 40\n---\n\n# P\n', encoding="utf-8")
    _register(repo, "PHASE-0040", rel)

    out = _run(repo, "SNAPSHOT.yaml", rel)
    assert "PHASE-0040" in out.stderr
    assert "DANGLING" not in out.stderr, out.stderr


def test_a_removed_entry_is_named_too(tmp_path: Path) -> None:
    """**Collision 3 is the one to learn from**: the repair for a stale
    diagnosis deleted a *valid* registration, and the local check was silent —
    a snapshot entry with no note is an error, a note with no entry is only a
    warning, so the asymmetry that caught the first mistake said nothing about
    the over-correction."""
    repo = _repo(tmp_path)
    (repo / "SNAPSHOT.yaml").write_text(
        SNAPSHOT.replace(
            '    FEAT-0001:\n      file: "docs/features/f/FEAT-0001-F.md"\n'
            "      status: done\n", ""),
        encoding="utf-8")
    out = _run(repo, "SNAPSHOT.yaml")
    assert "removed" in out.stderr and "FEAT-0001" in out.stderr, out.stderr


# ---- and what it must not do ---------------------------------------------

def test_a_close_out_that_does_not_touch_the_snapshot_says_nothing(
        tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "docs" / "features" / "f" / "FEAT-0001-F.md").write_text(
        NOTE + "\nedited\n", encoding="utf-8")
    out = _run(repo, "docs/features/f/FEAT-0001-F.md")
    assert out.returncode == 0, out.stderr
    assert "membership" not in out.stderr, out.stderr


def test_an_unchanged_membership_says_nothing(tmp_path: Path) -> None:
    """The common case: the snapshot's derived fields moved and its membership
    did not. A report that fires on every close-out is a report nobody reads."""
    repo = _repo(tmp_path)
    (repo / "SNAPSHOT.yaml").write_text(
        SNAPSHOT.replace('updated: "2026-08-21"', 'updated: "2026-08-22"'),
        encoding="utf-8")
    out = _run(repo, "SNAPSHOT.yaml")
    assert out.returncode == 0, out.stderr
    assert "membership" not in out.stderr, out.stderr


def test_it_reports_and_never_refuses(tmp_path: Path) -> None:
    """A close-out that stops because a shared file moved under it is
    automation people disable — the same reason dirty files outside the scope
    are left alone rather than treated as an error."""
    repo = _repo(tmp_path)
    _register(repo, "PHASE-0040", "docs/phases/PHASE-0040-P.md")
    out = _run(repo, "SNAPSHOT.yaml")
    assert out.returncode == 0, (out.returncode, out.stderr)
    assert _git(repo, "log", "--oneline").stdout.count("\n") == 2
