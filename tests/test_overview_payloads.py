"""Overview-rework payload additions (FEAT-0040 / TASK-0199).

Covers the three additive pieces: the resolved SNAPSHOT ``focus`` block in
``stats_payload``, issue ``severity`` in the slim item shape, and
``/api/cockpit/commits`` — including the hardening promises in the task's
DoD (fixed argv, clamped limit, graceful non-repo fallback) and the
undocumented-commit flag that carries FEAT-0022's guardrail per commit.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from project_os_cockpit import cockpit
from project_os_cockpit.index import Index


def _note(path: Path, fm: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for key, value in fm.items():
        lines.append(f"{key}: {json.dumps(value)}")
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body, encoding="utf-8")


def _workspace(tmp_path: Path, *, snapshot: str | None = None) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "features" / "x" / "FEAT-0001-X.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "Feature X",
        "status": "doing", "phase": "[[PHASE-001]]",
    })
    _note(docs / "features" / "x" / "plan" / "tasks" / "TASK-0001-Do.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "Do the thing",
        "status": "doing", "parent": "[[FEAT-0001]]",
    })
    _note(docs / "phases" / "PHASE-001-One.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "Phase One",
        "status": "active",
    })
    # Two issues: one with an explicit severity, one without (defaults low).
    _note(docs / "issues" / "ISS-0001-Sev.md", {
        "type": "[[issue]]", "id": "ISS-0001", "title": "Severe thing",
        "status": "open", "severity": "high", "parent": "[[FEAT-0001]]",
    })
    _note(docs / "issues" / "ISS-0002-Nosev.md", {
        "type": "[[issue]]", "id": "ISS-0002", "title": "Unrated thing",
        "status": "open", "parent": "[[FEAT-0001]]",
    })
    if snapshot is not None:
        (tmp_path / "SNAPSHOT.yaml").write_text(snapshot, encoding="utf-8")
    return docs


SNAPSHOT_WITH_FOCUS = """version: 1
focus:
  task: "TASK-0001"
  feature: "FEAT-0001"
  phase: "[[PHASE-001-One]]"
  issue: ""
  note: "2026-07-26 working the thing — some prose about it."

items:
  features: {}
"""


# ---- focus block --------------------------------------------------------

def test_focus_block_resolves_ids_against_the_index(tmp_path: Path) -> None:
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    index = Index.build(docs)

    focus = cockpit.focus_block(index)

    assert focus is not None
    items = focus["items"]
    # Empty slots (issue: "") are skipped, not emitted as blanks.
    assert set(items) == {"task", "feature", "phase"}
    assert items["task"]["title"] == "Do the thing"
    assert items["task"]["status"] == "doing"
    assert items["task"]["type"] == "task"
    assert items["task"]["rel"].endswith("TASK-0001-Do.md")
    assert items["task"]["done"] is False
    assert items["phase"]["id"] == "PHASE-001"


def test_focus_block_exposes_note_and_its_date(tmp_path: Path) -> None:
    """The staleness label needs the date the note convention puts first."""
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    focus = cockpit.focus_block(Index.build(docs))
    assert focus is not None
    assert focus["note_date"] == "2026-07-26"
    assert "working the thing" in focus["note"]


def test_focus_block_absent_snapshot_is_none(tmp_path: Path) -> None:
    docs = _workspace(tmp_path)  # no SNAPSHOT.yaml written
    assert cockpit.focus_block(Index.build(docs)) is None


def test_focus_block_unresolvable_id_keeps_the_id(tmp_path: Path) -> None:
    """A focus pointing at a deleted note degrades to the bare id rather
    than dropping the slot — the reader should see the dangling pointer."""
    docs = _workspace(tmp_path, snapshot=(
        'version: 1\nfocus:\n  task: "TASK-9999"\n  note: "2026-01-01 gone"\n'
    ))
    focus = cockpit.focus_block(Index.build(docs))
    assert focus is not None
    assert focus["items"]["task"] == {"id": "TASK-9999"}


def test_stats_payload_carries_focus(tmp_path: Path) -> None:
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    payload = cockpit.stats_payload(Index.build(docs))
    assert payload is not None
    assert payload["focus"]["items"]["feature"]["id"] == "FEAT-0001"


# ---- issue severity -----------------------------------------------------

def test_slim_issue_items_carry_severity(tmp_path: Path) -> None:
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    payload = cockpit.stats_payload(Index.build(docs))
    assert payload is not None
    issues = {
        child["id"]: child
        for phase in payload["phases"]
        for feature in phase["features"]
        for child in feature["children"]
        if child["type"] == "issue"
    }
    assert issues["ISS-0001"]["severity"] == "high"
    # Absent severity reads "low", matching the right pane (TASK-0035).
    assert issues["ISS-0002"]["severity"] == "low"


def test_non_issue_items_do_not_gain_a_severity_key(tmp_path: Path) -> None:
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    payload = cockpit.stats_payload(Index.build(docs))
    assert payload is not None
    tasks = [
        child
        for phase in payload["phases"]
        for feature in phase["features"]
        for child in feature["children"]
        if child["type"] == "task"
    ]
    assert tasks and all("severity" not in t for t in tasks)


# ---- commits ------------------------------------------------------------

def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True,
    )


def _git_repo(tmp_path: Path) -> tuple[Path, Path]:
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "Tester")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "docs: add the notes")
    # A code-only commit — the undocumented case.
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "code: tweak app")
    return tmp_path, docs


def test_commits_join_notes_by_rel_path(tmp_path: Path) -> None:
    root, docs = _git_repo(tmp_path)
    payload = cockpit.commits_payload(root, Index.build(docs))

    assert payload["available"] is True
    docs_commit = next(
        c for c in payload["commits"] if c["subject"] == "docs: add the notes"
    )
    ids = {item["id"] for item in docs_commit["items"]}
    assert {"FEAT-0001", "TASK-0001", "ISS-0001", "PHASE-001"} <= ids
    feature = next(i for i in docs_commit["items"] if i["id"] == "FEAT-0001")
    assert feature["status"] == "doing"
    assert feature["type"] == "feature"
    assert feature["done"] is False
    assert docs_commit["undocumented"] is False
    assert docs_commit["date"].count("-") == 2


def test_commit_touching_no_notes_is_flagged_undocumented(tmp_path: Path) -> None:
    """FEAT-0022's traceability guardrail, applied per commit."""
    root, docs = _git_repo(tmp_path)
    payload = cockpit.commits_payload(root, Index.build(docs))
    code_commit = next(
        c for c in payload["commits"] if c["subject"] == "code: tweak app"
    )
    assert code_commit["items"] == []
    assert code_commit["undocumented"] is True


def test_commits_limit_is_clamped(tmp_path: Path) -> None:
    """`limit` is the only caller-derived value; it never reaches git as a
    string and can't be used to widen the response beyond the cap."""
    root, docs = _git_repo(tmp_path)
    index = Index.build(docs)

    assert len(cockpit.commits_payload(root, index, limit=1)["commits"]) == 1
    # Junk and out-of-range values fall back / clamp rather than raising.
    for bogus in ("abc", None, -5, 10**6):
        payload = cockpit.commits_payload(root, index, limit=bogus)  # type: ignore[arg-type]
        assert payload["available"] is True
        assert len(payload["commits"]) <= cockpit.COMMITS_MAX_LIMIT


def test_commits_outside_a_git_repo_degrade(tmp_path: Path) -> None:
    docs = _workspace(tmp_path, snapshot=SNAPSHOT_WITH_FOCUS)
    payload = cockpit.commits_payload(tmp_path, Index.build(docs))
    assert payload == {
        "schema_version": cockpit.SCHEMA_VERSION,
        "available": False,
        "commits": [],
    }


def test_commits_ignore_non_note_paths(tmp_path: Path) -> None:
    """Files outside docs_root (and non-markdown files inside it) never
    resolve to items — the join is index-mediated, not path-guessed."""
    root, docs = _git_repo(tmp_path)
    (docs / "notes.txt").write_text("not a note\n", encoding="utf-8")
    (root / "README.md").write_text("# root readme\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "chore: mixed bag")
    payload = cockpit.commits_payload(root, Index.build(docs))
    mixed = next(c for c in payload["commits"] if c["subject"] == "chore: mixed bag")
    assert mixed["items"] == []
    assert mixed["undocumented"] is True
