"""Documentation history (FEAT-0052 / TASK-0255).

The overview's history band answered one question three ways — a weekly
edit count, the change notes, and the git log with notes as chips — and
all three read git or the filesystem as the *subject*. This payload
inverts it: the row is a note's **status transition** and the commit is
a **divider**.

Two properties carry the whole design and are asserted here rather than
described:

1. **A transition is not a touch.** Measured on this repo's phase-hygiene
   commit: 20 notes touched, 4 statuses changed. A touch-based list makes
   bookkeeping the largest event of the day.
2. **A commit with no transitions still appears.** It is the one a naive
   implementation drops for having no rows, and the one that most needs
   to be seen — code moved with nothing recording why (FEAT-0022).

The parser is exercised directly on log text rather than through a
fixture repo per case. Parsing is where this can be wrong, and a repo per
case would make the suite slow enough that nobody adds cases.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from project_os_cockpit import cockpit
from project_os_cockpit.cockpit import _parse_history_log, history_payload
from project_os_cockpit.index import Index

REPO_ROOT = Path(__file__).resolve().parents[1]
SEP = "\x01"


class _Rec:
    """Minimal stand-in for an index record."""

    def __init__(self, note_id: str, note_type: str = "task") -> None:
        self.note_id = note_id
        self.note_type = note_type
        self.title = f"{note_id} title"
        self.rel_path = f"tasks/{note_id}.md"
        self.status = "done"


def _resolve(path: str):  # type: ignore[no-untyped-def]
    name = path.rsplit("/", 1)[-1]
    return _Rec(name.split("-")[0] + "-" + name.split("-")[1]) if "-" in name else None


def _log(*commits: str) -> str:
    return "".join(commits)


def _commit(sha: str, subject: str, body: str = "") -> str:
    return f"{SEP}{sha}\t{sha}0000\t2026-07-30T10:00:00+00:00\tEdwin\t{subject}\n{body}"


def _file_diff(path: str, minus: str | None, plus: str | None) -> str:
    out = f"--- a/{path}\n+++ b/{path}\n@@ -6 +6 @@\n"
    if minus is not None:
        out += f"-status: {minus}\n"
    if plus is not None:
        out += f"+status: {plus}\n"
    return out


# ---- the parser -------------------------------------------------------

def test_a_moved_status_is_a_transition_with_both_ends() -> None:
    text = _log(_commit("aaa111", "close it",
                        _file_diff("docs/tasks/TASK-0001-X.md", "doing", "done")))
    commits = _parse_history_log(text, _resolve)
    assert len(commits) == 1
    t = commits[0]["transitions"][0]
    assert (t["from"], t["to"]) == ("doing", "done")
    assert t["created"] is False


def test_a_created_note_is_not_rendered_as_a_journey() -> None:
    """`+status: done` with no `-status:` means the note was BORN done.

    Most notes in a busy commit are written and closed in one pass, and
    an arrow would imply a history they never had.
    """
    text = _log(_commit("bbb222", "add it",
                        _file_diff("docs/tasks/TASK-0002-Y.md", None, "done")))
    t = _parse_history_log(text, _resolve)[0]["transitions"][0]
    assert t["created"] is True
    assert t["from"] is None
    assert t["to"] == "done"


def test_a_touch_that_changes_no_status_is_not_a_row() -> None:
    """The design's central claim, in miniature.

    A note whose `phase:` was corrected is not an event. Sixteen of the
    twenty notes in this repo's phase-hygiene commit were exactly that.
    """
    body = ("--- a/docs/tasks/TASK-0003-Z.md\n+++ b/docs/tasks/TASK-0003-Z.md\n"
            "@@ -7 +7 @@\n-phase: \"[[PHASE-999-Future]]\"\n"
            "+phase: \"[[PHASE-011-Unproven-Claims]]\"\n")
    commits = _parse_history_log(_log(_commit("ccc333", "re-home", body)), _resolve)
    assert commits[0]["transitions"] == []
    assert commits[0]["undocumented"] is True, (
        "a commit with no transitions must be reported, not dropped"
    )


def test_a_commit_with_no_transitions_is_still_returned() -> None:
    """The trap. A naive transition-based list drops it for having no
    rows — and a commit that moved code with nothing recording why is
    precisely the one worth seeing (FEAT-0022's guardrail)."""
    text = _log(
        _commit("ddd444", "code only", ""),
        _commit("eee555", "close it",
                _file_diff("docs/tasks/TASK-0004-W.md", "doing", "done")),
    )
    commits = _parse_history_log(text, _resolve)
    assert [c["sha"] for c in commits] == ["ddd444", "eee555"]
    assert commits[0]["undocumented"] is True
    assert commits[1]["undocumented"] is False


def test_one_commit_can_carry_several_transitions_one_per_file() -> None:
    body = (_file_diff("docs/tasks/TASK-0005-A.md", "doing", "done")
            + _file_diff("docs/tasks/TASK-0006-B.md", None, "backlog"))
    t = _parse_history_log(_log(_commit("fff666", "two", body)), _resolve)[0]
    assert len(t["transitions"]) == 2
    assert {x["to"] for x in t["transitions"]} == {"done", "backlog"}


def test_a_status_line_outside_any_file_is_ignored() -> None:
    """A commit *message* containing `+status: done` must not become a row."""
    text = _log(_commit("999zzz", "subject", "+status: done\n"))
    assert _parse_history_log(text, _resolve)[0]["transitions"] == []


def test_a_malformed_record_line_does_not_take_the_batch_down() -> None:
    text = f"{SEP}broken\n" + _commit(
        "aaa999", "ok", _file_diff("docs/tasks/TASK-0007-C.md", "doing", "done"))
    commits = _parse_history_log(text, _resolve)
    assert [c["sha"] for c in commits] == ["aaa999"]


# ---- against the real repository --------------------------------------

def test_the_payload_runs_on_this_repo_and_resolves_ids() -> None:
    index = Index.build(REPO_ROOT / "docs")
    payload = history_payload(REPO_ROOT, index, limit=10)
    assert payload["available"] is True
    assert payload["commits"], "this repo has history"
    ids = [t["id"] for c in payload["commits"] for t in c["transitions"]]
    assert any(i and i.startswith(("FEAT-", "TASK-", "ISS-", "PHASE-")) for i in ids), (
        "transitions resolve to note IDs, not bare paths"
    )


def test_transitions_are_fewer_than_touches_on_a_bookkeeping_commit() -> None:
    """The measurement the design rests on, asserted against real history.

    `cebee80` re-homed sixteen notes' `phase:` field and closed four
    things. The old commits tile shows 20 items for it; this shows 4.
    Skipped if that commit is not reachable (shallow clone, rewritten
    history) rather than asserted into a false failure.
    """
    probe = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "cat-file", "-e", "cebee80^{commit}"],
        capture_output=True, check=False,
    )
    if probe.returncode != 0:
        pytest.skip("cebee80 not in this clone's history")

    index = Index.build(REPO_ROOT / "docs")
    touched = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "show", "--name-only", "--format=", "cebee80"],
        capture_output=True, text=True, check=False,
    ).stdout.split()
    touched_notes = [p for p in touched if p.endswith(".md") and p.startswith("docs/")]

    payload = history_payload(REPO_ROOT, index, limit=40)
    match = [c for c in payload["commits"] if c["sha"].startswith("cebee80")]
    if not match:
        pytest.skip("cebee80 outside the fetched window")
    transitions = match[0]["transitions"]

    assert len(transitions) < len(touched_notes), (
        f"{len(transitions)} transitions vs {len(touched_notes)} notes touched — "
        "if these are equal the payload is counting touches, which is the "
        "thing this design replaced"
    )


def test_unavailable_rather_than_raising_outside_a_repo(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    payload = history_payload(tmp_path, Index.build(tmp_path / "docs"))
    assert payload["available"] is False
    assert payload["commits"] == [] and payload["uncommitted"] == []


def test_the_uncommitted_band_reflects_the_working_tree(tmp_path: Path) -> None:
    """"Not saved yet" is the half git history cannot answer."""
    repo = tmp_path / "r"
    (repo / "docs").mkdir(parents=True)
    (repo / "SNAPSHOT.yaml").write_text("counters: {}\n", encoding="utf-8")
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", "-C", str(repo), *a], capture_output=True, check=False)
    run("init", "-q")
    run("config", "user.email", "t@e.st")
    run("config", "user.name", "T")
    (repo / "docs" / "a.md").write_text("---\nstatus: doing\n---\n", encoding="utf-8")
    run("add", "-A")
    run("commit", "-qm", "first")

    index = Index.build(repo / "docs")
    assert history_payload(repo, index)["uncommitted"] == [], "clean tree, empty band"

    (repo / "docs" / "b.md").write_text("---\nstatus: done\n---\n", encoding="utf-8")
    band = history_payload(repo, index)["uncommitted"]
    assert [row["path"] for row in band] == ["docs/b.md"]
