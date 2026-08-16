"""The publication ladder — how far this project's work has travelled.

**Publication is the third phase** ([[ADR-0028]]), and it is the one the tool
has never had a surface for. Its obligations lived on `overview` — a view named
for *everything* — because there was nowhere else to put them.

Edwin asked for a release view and attached the question that decides its
shape: *"there are probably multiple types of releases, from committing,
pushing, deploying and actual versioned releases … should they all be shown in
this release view together with a history?"*

The fleet answers it. Measured across the twelve repos the cockpit renders on
2026-08-16:

===================  ==========================  =====  ==============================
rung                 who acts                    repos  live that day
===================  ==========================  =====  ==============================
``commit``           the agent, at close-out     12/12  --
``push``             the human, from the cockpit  8     7 commits across 4 repos
``deploy``           the human, elsewhere         2     your-applications.com at 34
``release``          the human, gated             3     your-trainer: 11 notes, 12 tags
===================  ==========================  =====  ==============================

So a ``Releases`` view would be **empty in 9 of 12 repos** — a permanent blank
button, the failure this project's `CLAUDE.md` records twice. The *ladder* is
universal: every repo commits.

**Three of the four rungs already existed.** `history_payload` returns
``remote_kind``, ``unpublished_count``, ``publication_known`` and a per-commit
``unpublished`` flag; since ISS-0168 the Push button sits with the commits it
publishes. What was missing is the fourth — ``git_state.py`` mentions "tag"
once, in a comment — and a home.

**Absent is not zero.** A rung the repo cannot reach is *omitted*, not rendered
empty: this project's standing rule, and the reason a repo with no remote reads
as complete rather than broken. A rung it *can* reach whose count is unknown
(`edankert.com`: a deploy remote with no upstream, so ``ahead`` is None) is a
row saying so — never a zero, which is the coercion ADR-0027's fourth admission
test exists to refuse and which shipped wrong once already.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import git_state

if TYPE_CHECKING:  # pragma: no cover
    from .index import Index

#: The ladder, in order. A rung's position is its meaning — work climbs.
RUNGS: tuple[str, ...] = ("commit", "push", "deploy", "release")

#: What each rung asks of a person, in the registry's vocabulary. `deploy` is
#: **named and refused** (Edwin, 2026-08-16): one fleet repo's only remote is a
#: server path, and pushing it publishes a live website. ADR-0027's third
#: admission test asks for an action the cockpit can offer **or name**; this is
#: the case that clause was written for.
RUNG_VERBS: dict[str, str] = {
    "commit": "Commit", "push": "Push", "deploy": "Deploy", "release": "Release",
}

_VERSION_RE = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


@dataclass
class Rung:
    """One rung, and what stands at it."""

    name: str
    #: False when this repo cannot reach it — the rung is then omitted
    #: entirely rather than rendered at zero.
    reachable: bool = True
    count: int = 0
    #: True when the rung is reachable but its count cannot be taken. Never
    #: collapses to `count == 0`.
    unknown: bool = False
    #: An action the cockpit offers here, or "" when it only names one.
    verb: str = ""
    #: Why nothing is offered, when nothing is.
    refused: str = ""
    detail: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)

    def payload(self) -> dict[str, Any]:
        return {
            "rung": self.name, "count": self.count, "unknown": self.unknown,
            "verb": self.verb, "refused": self.refused, "detail": self.detail,
            "rows": self.rows,
        }


def _tags(project_root: Path) -> list[dict[str, str]]:
    """Tags newest-first, or an empty list when git cannot say.

    Wrapped rather than trusted: a repo with no tags, a detached HEAD and an
    unreadable git dir must each yield nothing and take nothing down with them
    — one bad repo must not kill the fleet pass.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(project_root), "tag", "--sort=-creatordate",
             "--format=%(refname:short)%09%(creatordate:short)"],
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):  # pragma: no cover
        return []
    if out.returncode != 0:
        return []
    tags: list[dict[str, str]] = []
    for line in out.stdout.splitlines():
        name, _, when = line.partition("\t")
        if name.strip():
            tags.append({"name": name.strip(), "when": when.strip()})
    return tags


def _releases(index: "Index") -> list[dict[str, Any]]:
    """`REL-*` notes, newest id first."""
    out: list[dict[str, Any]] = []
    for record in index.notes_by_type("release"):
        if record.rel_path.startswith("__templates__/"):
            continue
        out.append({
            "id": record.note_id or "",
            "title": record.title or "",
            "status": (record.status or "").strip().lower(),
            "version": str(record.frontmatter.get("version") or "").strip(),
            # `preparing:` is FRONTMATTER, not a status (FEAT-0105 /
            # TASK-0438). STATUSES.md allows a release only draft / released /
            # reverted and is template-owned, so adding vocabulary there would
            # report as divergence on the next sync. DES-0006 established this
            # exact pattern and obligations.py already documents it for
            # features: *"`acceptance: requested` in frontmatter, not a
            # status."* One precedent, applied again.
            "features": [
                str(f) for f in (record.frontmatter.get("features") or [])
            ],
            "preparing": bool(str(
                record.frontmatter.get("preparing") or "",
            ).strip()),
            "rel": record.rel_path,
        })
    out.sort(key=lambda r: str(r["id"]), reverse=True)
    return out


def _version_key(version: str) -> tuple[int, ...]:
    """`"2.1.6"` -> `(2, 1, 6)`; unparseable -> `()`, which sorts lowest."""
    found = _VERSION_RE.search(version or "")
    if not found:
        return ()
    return tuple(int(part) for part in found.group(1).split("."))


def preparing(index: "Index") -> dict[str, Any] | None:
    """The release a person has declared they intend to ship, or None.

    **Not merely a `draft`.** If a release is always open — which is what
    FEAT-0105 gives you — and the gate asked whenever one existed, the gate
    would ask **forever**: the self-re-arming badge ADR-0027 excludes
    staleness for, and the failure PHASE-034 was opened to avoid producing.
    Being *open* and being *prepared for ship* are different facts and only
    the second is a debt.

    `STATUSES.md` documents a release's ``draft`` as *"prepared and verified,
    not yet live"*. That is a release in preparation, it has been representable
    since the vocabulary was written, and **nothing has ever read it** — which
    is why the acceptance gate had no subject and mounted only on a note a
    reader had to already know to open.

    **A draft behind a shipped version is not in preparation.** Found by
    running this against the fleet rather than against a fixture: `your-trainer`
    carries `REL-0008` at `draft`, version **2.0.2**, while 2.0.5, 2.1.0 and
    2.1.6 have all shipped since. Gating on it would have said *"60 checks
    stand between 2.0.2 and shipping"* about a version three releases in the
    past — and, worse, it would have said it **forever**, which is precisely
    the self-re-arming badge ADR-0027 refuses and that this whole phase exists
    to avoid producing.

    Such a draft is stale record-keeping in the repo that owns it. It is
    reported by :func:`stale_drafts` so it stays visible, and it does not gate.
    """
    for release in open_releases(index):
        if release["preparing"]:
            return release
    return None


def open_releases(index: "Index") -> list[dict[str, Any]]:
    """Drafts a shipped version has not overtaken — open or preparing."""
    releases = _releases(index)
    shipped = max(
        (_version_key(r["version"]) for r in releases if r["status"] == "released"),
        default=(),
    )
    live = [
        r for r in releases
        if r["status"] == "draft" and _version_key(r["version"]) > shipped
    ]
    live.sort(key=lambda r: _version_key(r["version"]), reverse=True)
    return live


def stale_drafts(index: "Index") -> list[dict[str, Any]]:
    """Drafts a later release has already overtaken.

    Named rather than dropped: a `draft` note that a shipped version passed is
    a real thing to fix, and silently ignoring it would replace one wrong
    signal with no signal.
    """
    releases = _releases(index)
    shipped = max(
        (_version_key(r["version"]) for r in releases if r["status"] == "released"),
        default=(),
    )
    return [
        r for r in releases
        if r["status"] == "draft" and _version_key(r["version"]) <= shipped
    ]


def ladder(project_root: Path, index: "Index") -> list[Rung]:
    """Every rung this repo reaches, in order."""
    try:
        state = git_state.read(project_root)
    except OSError:                       # pragma: no cover — unreadable repo
        state = git_state.GitState(
            remote=None, kind="none", ahead=None, commits=(), dirty=0,
        )

    rungs: list[Rung] = []

    # ---- commit: every repo reaches it -----------------------------------
    # **No verb, deliberately.** ADR-0027's first admission test is that a
    # PERSON must discharge it, and committing is the agent's — `close-out
    # commits its own work` (FEAT-0055). The rung is shown because it is the
    # bottom of the ladder and the only one every repo reaches; it is state,
    # not a debt.
    rungs.append(Rung(
        name="commit", count=state.dirty, verb="",
        detail=(
            f"{state.dirty} uncommitted note(s) — the agent commits these at "
            "close-out" if state.dirty else "nothing uncommitted"
        ),
    ))

    # ---- push / deploy: whichever remote this repo has --------------------
    # A repo has exactly one remote kind, so exactly one of these is reachable
    # — and merging them would put two things a person must treat differently
    # behind one number.
    for name, kind in (("push", "backup"), ("deploy", "deploy")):
        if state.kind != kind:
            rungs.append(Rung(name=name, reachable=False))
            continue
        rung = Rung(name=name, verb=RUNG_VERBS[name], detail=state.remote or "")
        if name == "deploy":
            rung.verb = ""
            rung.refused = (
                "this remote is a deployment target, not a backup — publishing "
                "it puts work live, so the cockpit names it and never sends it"
            )
        if state.ahead is None:
            rung.unknown = True
            rung.detail = "no upstream is set, so nothing can say what is unpublished"
        else:
            rung.count = len(state.commits)
            rung.rows = [
                {"id": c.sha, "title": c.subject, "detail": c.when}
                for c in state.commits
            ]
            # Absent at zero applies to the ASK as well as to the row: a rung
            # with nothing at it is still shown — that is the answer — but it
            # does not claim to need a person. A permanent `To push` on a repo
            # with nothing to push is the badge that re-arms itself.
            if not rung.count:
                rung.verb = ""
        rungs.append(rung)

    # ---- release: notes and tags -----------------------------------------
    releases = _releases(index)
    tags = _tags(project_root)
    if not releases and not tags:
        rungs.append(Rung(name="release", reachable=False))
    else:
        versions = {r["version"] for r in releases if r["version"]}
        rows: list[dict[str, Any]] = [
            {
                "id": r["id"], "title": r["title"], "status": r["status"],
                "detail": r["version"], "rel": r["rel"],
                # A tag naming the same version, so a release note and the tag
                # that shipped it read as one thing rather than two lists.
                "tagged": any(
                    _VERSION_RE.search(t["name"])
                    and _VERSION_RE.search(t["name"]).group(1) == r["version"]
                    for t in tags
                ),
            }
            for r in releases
        ]
        # A tag with no note is shown as itself rather than hidden — the note
        # is the record, but the tag is what actually shipped.
        for tag in tags:
            found = _VERSION_RE.search(tag["name"])
            if found and found.group(1) in versions:
                continue
            rows.append({
                "id": tag["name"], "title": "tag with no release note",
                # `released` rather than blank: a tag IS a thing that shipped,
                # and an empty status made the whole rung read as open work,
                # so the record never folded away (Edwin: *"the other views
                # hide completed items, so you can only see the next/current
                # items to work on"*).
                "status": "released", "detail": tag["when"], "rel": "",
                "tagged": True,
            })
        draft = preparing(index)
        rungs.append(Rung(
            name="release", count=len(releases), verb="",
            detail=(
                f"{draft['id']} in preparation" if draft
                else f"{len(tags)} tag(s)"
            ),
            rows=rows,
        ))
    return rungs


def payload(project_root: Path, index: "Index") -> dict[str, Any]:
    """The ladder as data, for the Publication view."""
    rungs = ladder(project_root, index)
    draft = preparing(index)
    return {
        "rungs": [r.payload() for r in rungs if r.reachable],
        # Named so a surface can say "this repo does not deploy" rather than
        # leaving the reader to infer it from an absence.
        "unreachable": [r.name for r in rungs if not r.reachable],
        "preparing": draft,
        # Visible, and not gating.
        "stale_drafts": stale_drafts(index),
    }


def release_payload(
    project_root: Path, index: "Index", release_id: str = "next",
) -> dict[str, Any]:
    """One answer for the release page (FEAT-0106 / TASK-0440).

    What is in this release, what state it is in, and what stands between it
    and shipping — assembled from the computations that already exist rather
    than from new ones. `unreleased_payload` for what has not shipped,
    `acceptance.gate_payload` for the gate.

    ``next`` answers **even when no release note exists**, which is the
    ordinary case: the open release is derived and nothing is written until a
    person declares one.
    """
    from . import acceptance
    from .cockpit import unreleased_payload

    wanted = (release_id or "next").strip()
    releases = _releases(index)
    held: dict[str, Any] | None = None
    if wanted.lower() == "next":
        live = open_releases(index)
        held = live[0] if live else None
    else:
        held = next((r for r in releases if r["id"] == wanted), None)

    shipped = held is not None and held["status"] == "released"
    if shipped:
        # A shipped release names what it carried; the derived set has moved
        # on. The frozen list is the record and must not be recomputed.
        contents = {
            "kind": "frozen",
            "ids": list(held.get("features") or []),
            "count": len(held.get("features") or []),
            "since": "",
        }
    else:
        # `unreleased_payload`'s own keys: `items` and `since` (FEAT-0072).
        # Read them rather than inventing near-misses — a second vocabulary
        # for one computation is how two surfaces come to disagree.
        unshipped = unreleased_payload(index)
        rows = unshipped.get("items") or []
        since = unshipped.get("since") or {}
        contents = {
            "kind": "derived",
            "count": int(unshipped.get("count") or 0),
            "since": since.get("id", "") if isinstance(since, dict) else str(since),
            "rows": rows,
        }

    gate = acceptance.gate_payload(index.docs_root)
    return {
        "id": held["id"] if held else "",
        "version": held["version"] if held else "",
        "status": held["status"] if held else "",
        "preparing": bool(held and held["preparing"]),
        "exists": held is not None,
        "title": held["title"] if held else "Next release",
        "rel": held["rel"] if held else "",
        "contents": contents,
        "gate": gate,
        "stale_drafts": stale_drafts(index),
    }
