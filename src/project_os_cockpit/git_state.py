"""What a repo has that its remote does not (TASK-0417).

The sidecar answers this for **its own** repo, because the obligation registry
lives here and a badge cannot count what the process serving it cannot see.
The Electron shell asks `git` directly for the whole fleet (`desktop/src/ipc/
git.ts`) — a different consumer with a different scope, and the one that
actually runs `git push`, which is why it will not trust a classification that
arrived over IPC.

The classification therefore exists in two languages on purpose. What must not
exist twice is the *rule*, so the table below and its counterpart in `git.ts`
are asserted against the same set of URLs in both suites.

`ahead` is None when there is no upstream to be ahead **of**, which is not the
same as being up to date and must never render as such (ADR-0027 test 4:
absent-at-zero means an unknown count is indistinguishable from nothing owed,
so "I cannot tell" may not be reported as a number).
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

#: Hosts whose remotes are a backup/forge rather than a deployment.
FORGE_HOSTS = ("github.com", "gitlab.com", "bitbucket.org", "codeberg.org")

#: How long a reading stays fresh. The registry is walked on every nav change,
#: and `git log` per keystroke would be a subprocess storm; a commit is not
#: news for a few seconds.
CACHE_SECONDS = 10.0

#: Unpushed commits are read for their subjects, not only counted, because the
#: obligation's rows ARE the commits (ADR-0020: an obligation lives with its
#: subject).
#:
#: **Deliberately uncapped.** A cap was written here first and removed the same
#: hour: the registry's invariant is that a count IS the length of its rows —
#: that is the whole repair TASK-0416 made — and a capped list with a separate
#: total reintroduces exactly the disagreement it removed, in the one place a
#: reader would never think to check. `git log` over a few hundred commits is
#: milliseconds, and the 5s timeout bounds the pathological case.


def remote_kind(url: str) -> str:
    """``backup`` | ``deploy`` | ``none``, from the URL rather than a setting.

    This decides whether anything may push automatically, so it is derived and
    not configured: a setting can be wrong, and being wrong here means
    deploying a website. Unknown shapes are **deploy** — the safe default for
    "I do not recognise this" is "do not publish to it".
    """
    u = (url or "").strip()
    if not u:
        return "none"
    lowered = u.lower()
    for host in FORGE_HOSTS:
        if f"//{host}/" in lowered or f"@{host}:" in lowered:
            return "backup"
    return "deploy"


@dataclass(frozen=True)
class Commit:
    """One unpublished commit — the subject of a publication obligation."""

    sha: str
    subject: str
    when: str


@dataclass(frozen=True)
class GitState:
    remote: str | None
    kind: str                       # backup | deploy | none
    ahead: int | None
    commits: tuple[Commit, ...]     # newest first, capped at MAX_COMMITS


_EMPTY = GitState(remote=None, kind="none", ahead=None, commits=())

_cache: dict[str, tuple[float, GitState]] = {}


def _git(project_root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(  # noqa: S603 — fixed argv, no shell
            ["git", "-C", str(project_root), *args],
            capture_output=True, text=True, timeout=5.0, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def read(project_root: Path, *, now: float | None = None) -> GitState:
    """Publication state for one repo, cached for :data:`CACHE_SECONDS`."""
    key = str(project_root)
    stamp = time.monotonic() if now is None else now
    hit = _cache.get(key)
    if hit is not None and stamp - hit[0] < CACHE_SECONDS:
        return hit[1]

    state = _read_uncached(project_root)
    _cache[key] = (stamp, state)
    return state


def clear_cache() -> None:
    """Drop every cached reading — for tests, and for a workspace that moved."""
    _cache.clear()


def _read_uncached(project_root: Path) -> GitState:
    if not (project_root / ".git").exists():
        return _EMPTY

    url = _git(project_root, "remote", "get-url", "origin")
    if url is None:
        # No `origin`, but there may be another remote — and if it is a deploy
        # target, that is exactly what the caller needs to know.
        first = (_git(project_root, "remote") or "").splitlines()
        url = _git(project_root, "remote", "get-url", first[0]) if first else None
    kind = remote_kind(url or "")
    if kind == "none":
        # Nothing to be ahead of. A different and worse fact than "nothing to
        # publish", and it keeps its own shape rather than reporting zero.
        return _EMPTY

    counted = _git(project_root, "rev-list", "--count", "@{u}..HEAD")
    try:
        ahead = int(counted) if counted is not None else None
    except ValueError:
        ahead = None
    if not ahead:
        return GitState(remote=url, kind=kind, ahead=ahead, commits=())

    # `%x1f` (unit separator) rather than a printable delimiter: a commit
    # subject may contain any of them, and splitting on `|` would truncate the
    # one commit whose message explained something.
    raw = _git(
        project_root, "log", "@{u}..HEAD", "--format=%h%x1f%s%x1f%cs",
    ) or ""
    commits: list[Commit] = []
    for line in raw.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        commits.append(Commit(sha=parts[0], subject=parts[1], when=parts[2]))
    return GitState(remote=url, kind=kind, ahead=ahead, commits=tuple(commits))
