"""Per-turn checkpoints — an undo unit smaller than a session (FEAT-0078).

[[RISK-0006]]'s first hazard is **compounding judgment**: a wrong assumption at
hour one is the context of every decision after it, and unattended wrongness
compounds until somebody reads the digest. Today the only unit of undo is the
close-out commit — the whole session's work, or nothing.

A checkpoint per agent turn turns *"the worker went wrong somewhere in three
hours"* from an archaeology problem into a slider.

**Outside `refs/heads`, and outside every push path.** Checkpoints are local
safety, not history to publish: they live under ``refs/cockpit/turns/`` so a
branch listing, a `git push`, and the fleet roll-up's push action never see
them. Publishing is a person's deliberate act (FEAT-0055's line) and a
checkpoint is the opposite of deliberate — it is taken automatically, dozens of
times an hour.

**Untracked files are included.** An agent's damage is often a file it *added*,
and a checkpoint that captured only tracked changes would restore a tree still
carrying it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

#: The namespace. Deliberately not under `refs/heads` or `refs/tags`: both are
#: pushed by default and shown by `git branch`, and a hundred turn refs in a
#: branch list is a tool nobody keeps.
REF_NAMESPACE = "refs/cockpit/turns"

#: Pruning, stated where it is set rather than in a config nobody reads.
#: A day of hard use is a few hundred turns; keeping the most recent 200 keeps
#: roughly that, and anything older has been superseded by a commit anyway.
MAX_CHECKPOINTS = 200

_TIMEOUT = 10.0


def _git(root: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 — fixed argv, no shell
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, timeout=_TIMEOUT, check=check,
    )


def available(root: Path) -> bool:
    return (root / ".git").exists()


def capture(root: Path, *, label: str = "", session: str = "") -> dict[str, Any]:
    """Capture the working tree, including untracked files, as one ref.

    Uses a temporary index so the real one is untouched — an agent mid-`git
    add` must not have its staging area rewritten by a checkpoint it did not
    ask for. That is the difference between a safety net and a second actor.
    """
    if not available(root):
        return {"ok": False, "error": "not a git repository"}

    import os
    import tempfile

    env = dict(os.environ)
    with tempfile.TemporaryDirectory() as tmp:
        env["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
        add = subprocess.run(  # noqa: S603
            ["git", "-C", str(root), "add", "-A", "--force", "."],
            capture_output=True, text=True, timeout=_TIMEOUT, check=False, env=env,
        )
        if add.returncode != 0:
            return {"ok": False, "error": add.stderr.strip()[:200]}
        tree = subprocess.run(  # noqa: S603
            ["git", "-C", str(root), "write-tree"],
            capture_output=True, text=True, timeout=_TIMEOUT, check=False, env=env,
        )
        if tree.returncode != 0:
            return {"ok": False, "error": tree.stderr.strip()[:200]}
        tree_sha = tree.stdout.strip()

    parent = _git(root, "rev-parse", "HEAD").stdout.strip()
    message = f"checkpoint: {label or 'turn'}" + (f" [{session}]" if session else "")
    args = ["commit-tree", tree_sha, "-m", message]
    if parent:
        args += ["-p", parent]
    made = _git(root, *args)
    if made.returncode != 0:
        return {"ok": False, "error": made.stderr.strip()[:200]}
    sha = made.stdout.strip()

    ref = f"{REF_NAMESPACE}/{sha[:12]}"
    updated = _git(root, "update-ref", ref, sha)
    if updated.returncode != 0:
        return {"ok": False, "error": updated.stderr.strip()[:200]}
    prune(root)
    return {"ok": True, "sha": sha, "ref": ref, "label": label, "session": session}


def listing(root: Path, limit: int = 50) -> list[dict[str, Any]]:
    """Checkpoints, newest first."""
    if not available(root):
        return []
    out = _git(
        root, "for-each-ref", f"--count={limit}", "--sort=-creatordate",
        "--format=%(refname)%09%(objectname)%09%(creatordate:iso-strict)%09%(contents:subject)",
        REF_NAMESPACE,
    )
    rows: list[dict[str, Any]] = []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        rows.append({
            "ref": parts[0], "sha": parts[1], "at": parts[2], "subject": parts[3],
        })
    return rows


def prune(root: Path, keep: int = MAX_CHECKPOINTS) -> int:
    """Drop the oldest refs beyond `keep`. Returns how many went."""
    rows = listing(root, limit=keep + 500)
    dropped = 0
    for row in rows[keep:]:
        if _git(root, "update-ref", "-d", row["ref"]).returncode == 0:
            dropped += 1
    return dropped
