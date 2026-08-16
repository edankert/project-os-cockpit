"""The ladder is non-empty in every repo (TST-0027 / FEAT-0102).

The Publication view's whole justification over a `Releases` view is that it is
never empty: a `Releases` mode would be blank in **9 of 12** repos, while every
repo commits. That claim is a property of the payload across a real fleet, so
it is asserted against one — the four *shapes* are pinned on fixtures, because
they must hold whatever the fleet looks like next month.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import cockpit, publication
from project_os_cockpit.index import Index

FLEET = Path.home() / "Dev" / "repos"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True,
                   capture_output=True, text=True)


def _repo(tmp_path: Path, *, remote: str | None = None) -> Path:
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    _git(root.parent, "init", "-q", str(root))
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "T")
    (root / "docs" / "seed.md").write_text("x\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "seed")
    if remote:
        _git(root, "remote", "add", "origin", remote)
    return root


def _rung(payload: dict, name: str) -> dict | None:
    for rung in payload["rungs"]:
        if rung["rung"] == name:
            return rung
    return None


def _release(root: Path, rid: str, status: str, version: str) -> None:
    d = root / "docs" / "releases"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}-R.md").write_text(
        f'---\ntype: "[[release]]"\nid: {rid}\ntitle: "R"\n'
        f'status: {status}\nversion: "{version}"\n---\n', encoding="utf-8",
    )


# ---- 1-4: the four shapes ------------------------------------------------


def test_a_backup_remote_with_nothing_ahead_is_shown_and_clear(
    tmp_path: Path,
) -> None:
    """A forge URL **and** a real upstream ref.

    Two drafts of this fixture were wrong, each in a way the code was right
    about. Adding a remote with no tracking branch gave `unknown` — correct,
    and it is the neighbouring shape below. Pointing it at a local bare repo
    gave the **deploy** rung, because `remote_kind` treats an unrecognised URL
    shape as a deployment target on purpose: *"the safe default for 'I do not
    recognise this' is 'do not publish to it'."*

    So the upstream ref is created directly against a forge URL — which is the
    only combination that produces the state this test names.
    """
    root = _repo(tmp_path, remote="https://github.com/e/x.git")
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    branch = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    _git(root, "update-ref", f"refs/remotes/origin/{branch}", head)
    _git(root, "branch", f"--set-upstream-to=origin/{branch}", branch)
    payload = publication.payload(root, Index.build(root / "docs"))
    push = _rung(payload, "push")
    assert push is not None, "a reachable rung must be present"
    assert push["unknown"] is False
    assert push["count"] == 0
    # Shown, and not asking — absent-at-zero applies to the ASK, not the rung.
    assert push["verb"] == ""


def test_a_repo_with_no_remote_omits_the_rung_rather_than_zeroing_it(
    tmp_path: Path,
) -> None:
    """Absent, not present-at-zero — this project's standing rule. The repo
    still reaches rung 1, so the view reads as complete rather than broken."""
    root = _repo(tmp_path)
    payload = publication.payload(root, Index.build(root / "docs"))
    assert _rung(payload, "push") is None
    assert _rung(payload, "deploy") is None
    assert "push" in payload["unreachable"]
    assert _rung(payload, "commit") is not None, "every repo reaches commit"


def test_an_unknown_count_is_a_row_and_never_a_zero(tmp_path: Path) -> None:
    """`edankert.com`'s shape: a deploy remote with no upstream, so `ahead` is
    None. This was coerced to zero on two renderer surfaces after a repair that
    fixed only Python, and all three surfaces silently reported nothing owed."""
    root = _repo(tmp_path, remote="root@10.0.0.1:/srv/site.git")
    payload = publication.payload(root, Index.build(root / "docs"))
    deploy = _rung(payload, "deploy")
    assert deploy is not None
    assert deploy["unknown"] is True
    assert deploy["count"] == 0, "count is meaningless while unknown…"
    assert "no upstream" in deploy["detail"], "…so the row says so"


def test_a_deploy_remote_is_named_and_never_offered(tmp_path: Path) -> None:
    """One fleet repo's only remote is a server path and pushing it publishes
    a live website (Edwin, 2026-08-16). ADR-0027's third admission test asks
    for an action the cockpit can offer **or name**; this is that case."""
    root = _repo(tmp_path, remote="root@10.0.0.1:/srv/site.git")
    payload = publication.payload(root, Index.build(root / "docs"))
    deploy = _rung(payload, "deploy")
    assert deploy["verb"] == "", "a deploy rung must offer nothing"
    assert deploy["refused"], "and must say why"


# ---- 5-8: the release rung ----------------------------------------------


def test_no_releases_and_no_tags_leaves_the_rung_unreached(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    payload = publication.payload(root, Index.build(root / "docs"))
    assert _rung(payload, "release") is None
    assert "release" in payload["unreachable"]


def test_a_draft_release_is_the_one_in_preparation(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    _release(root, "REL-0001", "released", "1.0.0")
    _release(root, "REL-0002", "draft", "1.1.0")
    draft = publication.preparing(Index.build(root / "docs"))
    assert draft is not None and draft["id"] == "REL-0002"


def test_a_draft_a_shipped_version_has_overtaken_does_not_gate(
    tmp_path: Path,
) -> None:
    """Found by running against the fleet rather than a fixture.

    `your-trainer` carries REL-0008 at `draft`, version **2.0.2**, while 2.0.5,
    2.1.0 and 2.1.6 have all shipped. Gating on it would claim 60 checks stand
    between 2.0.2 and shipping — about a version three releases in the past,
    and it would claim it forever, which is the self-re-arming badge ADR-0027
    refuses.
    """
    root = _repo(tmp_path)
    _release(root, "REL-0008", "draft", "2.0.2")
    _release(root, "REL-0012", "released", "2.1.6")
    index = Index.build(root / "docs")
    assert publication.preparing(index) is None
    # Named, not dropped: a draft a release overtook is a real thing to fix.
    assert [d["id"] for d in publication.stale_drafts(index)] == ["REL-0008"]


def test_a_tag_with_no_note_and_a_note_with_no_tag_are_both_shown(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path, remote="https://github.com/e/x.git")
    _release(root, "REL-0001", "released", "1.0.0")
    _git(root, "tag", "v2.0.0")
    payload = publication.payload(root, Index.build(root / "docs"))
    rows = {str(r["id"]) for r in _rung(payload, "release")["rows"]}
    assert "REL-0001" in rows, "a note with no tag"
    assert "v2.0.0" in rows, "a tag with no note"


def test_a_broken_repo_yields_what_it_can_without_raising(
    tmp_path: Path,
) -> None:
    """One bad repo must not take the fleet pass down."""
    root = tmp_path / "notgit"
    (root / "docs").mkdir(parents=True)
    payload = publication.payload(root, Index.build(root / "docs"))
    assert _rung(payload, "commit") is not None
    assert publication._tags(root) == []


# ---- 9-11: the fleet sweep ----------------------------------------------


def _fleet_repos() -> list[Path]:
    if not FLEET.is_dir():
        return []
    return [
        d for d in sorted(FLEET.iterdir())
        if (d / "SNAPSHOT.yaml").exists() and (d / "docs").is_dir()
    ]


@pytest.mark.skipif(not _fleet_repos(), reason="no discovered fleet")
def test_the_ladder_is_non_empty_in_every_discovered_repo() -> None:
    """The claim the whole view rests on.

    **Fails on a repo it cannot read rather than skipping it** — a sweep that
    quietly skips is how "non-empty in every repo" becomes true only of the
    repos it looked at.
    """
    empty: list[str] = []
    for root in _fleet_repos():
        payload = publication.payload(root, Index.build(root / "docs"))
        if not payload["rungs"]:
            empty.append(root.name)
    assert empty == [], empty


@pytest.mark.skipif(not _fleet_repos(), reason="no discovered fleet")
def test_every_repo_reaches_the_commit_rung() -> None:
    """Which is why the ladder is universal and `Releases` would not have
    been: measured 2026-08-16, commit 12/12, push 8, deploy 2, release 3."""
    for root in _fleet_repos():
        payload = publication.payload(root, Index.build(root / "docs"))
        assert _rung(payload, "commit") is not None, root.name


@pytest.mark.skipif(not _fleet_repos(), reason="no discovered fleet")
def test_the_publication_view_renders_in_every_repo() -> None:
    for root in _fleet_repos():
        index = Index.build(root / "docs")
        groups = cockpit.nav_payload(
            index, "publication", project_root=root,
        )["groups"]
        assert groups, root.name
        assert all(g["items"] for g in groups), root.name


def test_no_route_from_this_view_can_push_a_deploy_remote(
    tmp_path: Path,
) -> None:
    """Enumerated, the way the loopback guard enumerates."""
    root = _repo(tmp_path, remote="root@10.0.0.1:/srv/site.git")
    groups = cockpit.nav_payload(
        Index.build(root / "docs"), "publication", project_root=root,
    )["groups"]
    deploy = [g for g in groups if g["key"] == "rung-deploy"]
    assert deploy, "the rung must be present"
    assert not deploy[0].get("needs_human"), "a refused rung must not ask"
    assert deploy[0].get("refused")
    assert "owed_verb" not in deploy[0]


# ---- 12-13: reported from use, 2026-08-16 -------------------------------


def test_every_publication_row_is_clickable(tmp_path: Path) -> None:
    """Edwin, opening the view: *"not all the left-pane items are
    selectable."*

    A reachable rung with nothing at it still renders — that IS the answer
    ("nothing to push") — but its row carried `url: None`, and a row that does
    not respond to a click reads as a broken row rather than an empty one.
    """
    root = _repo(tmp_path, remote="https://github.com/e/x.git")
    _release(root, "REL-0001", "released", "1.0.0")
    groups = cockpit.nav_payload(
        Index.build(root / "docs"), "publication", project_root=root,
    )["groups"]
    dead = [
        (g["label"], i.get("title"))
        for g in groups for i in g["items"] if not i.get("url")
    ]
    assert dead == [], dead


def test_publication_does_not_also_receive_a_needs_you_group(
    tmp_path: Path,
) -> None:
    """Edwin: *"why in the needs you section"*.

    The view leads with the ladder and gathers what it owes into rungs, so a
    prepended `Needs you` put the one unpushed commit on screen twice — under
    `Needs you` and under `To push · 1`. That is ISS-0068's failure, which
    ADR-0025 permits only as a shortcut from a view that does not otherwise
    show the row.
    """
    root = _repo(tmp_path, remote="https://github.com/e/x.git")
    groups = cockpit.nav_payload(
        Index.build(root / "docs"), "publication", project_root=root,
    )["groups"]
    assert [g for g in groups if g["key"] == "needs-you"] == []
    assert "publication" in cockpit._VIEWS_THAT_ALREADY_GATHER
