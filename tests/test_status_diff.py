"""Status-diff layer (FEAT-0036 / TASK-0162, TST-0018).

A note save that changes frontmatter `status` emits exactly one
`cockpit:status-change`; saves without a status change, and a note's
first appearance after a cold seed, emit nothing.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit.events import ControlEvent, EventBus, FileEvent
from project_os_cockpit.index import Index
from project_os_cockpit.status_diff import StatusTracker


def _note(root: Path, rel: str, nid: str, status: str, ntype: str = "task") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f'---\ntype: "[[{ntype}]]"\nid: {nid}\ntitle: "T {nid}"\n'
        f'status: {status}\n---\n\nbody\n',
        encoding="utf-8",
    )
    return p


def _setup(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    _note(docs, "features/f/plan/tasks/TASK-0001.md", "TASK-0001", "backlog")
    index = Index.build(docs)
    bus = EventBus()
    events: list[ControlEvent] = []
    bus.subscribe(lambda e: events.append(e) if isinstance(e, ControlEvent) else None)
    st = StatusTracker(docs, bus)
    st.seed(index)
    bus.subscribe(st.on_event)
    return docs, bus, events, st


def _save(bus: EventBus, abs_path: Path, docs: Path, kind: str = "modified") -> None:
    bus.publish(FileEvent(kind=kind, rel_path=str(abs_path.relative_to(docs)), abs_path=abs_path))


def test_status_change_emits_one_event(tmp_path: Path):
    docs, bus, events, st = _setup(tmp_path)
    p = _note(docs, "features/f/plan/tasks/TASK-0001.md", "TASK-0001", "doing")
    _save(bus, p, docs)
    changes = [e for e in events if e.event_type == "cockpit:status-change"]
    assert len(changes) == 1
    d = changes[0].data
    assert d["id"] == "TASK-0001" and d["from"] == "backlog" and d["to"] == "doing"
    assert d["type"] == "task"
    trans = st.transitions()
    assert trans and trans[0]["id"] == "TASK-0001" and trans[0]["to"] == "doing"


def test_no_status_change_is_silent(tmp_path: Path):
    docs, bus, events, st = _setup(tmp_path)
    # Rewrite the same status (body edit) — no transition.
    p = _note(docs, "features/f/plan/tasks/TASK-0001.md", "TASK-0001", "backlog")
    _save(bus, p, docs)
    assert [e for e in events if e.event_type == "cockpit:status-change"] == []
    assert st.transitions() == []


def test_first_appearance_is_silent(tmp_path: Path):
    docs, bus, events, st = _setup(tmp_path)
    # A brand-new note not present at seed time = creation, not a move.
    p = _note(docs, "issues/ISS-0001.md", "ISS-0001", "open", ntype="issue")
    _save(bus, p, docs, kind="created")
    assert [e for e in events if e.event_type == "cockpit:status-change"] == []
    # …but a subsequent real change on it now emits.
    p = _note(docs, "issues/ISS-0001.md", "ISS-0001", "fixed", ntype="issue")
    _save(bus, p, docs)
    changes = [e for e in events if e.event_type == "cockpit:status-change"]
    assert len(changes) == 1 and changes[0].data["to"] == "fixed"


def test_deleted_and_unreadable_are_ignored(tmp_path: Path):
    docs, bus, events, st = _setup(tmp_path)
    p = docs / "features/f/plan/tasks/TASK-0001.md"
    _save(bus, p, docs, kind="deleted")
    assert [e for e in events if e.event_type == "cockpit:status-change"] == []
    # Unreadable file (a modified event pointing at a path that no longer
    # parses) is swallowed, not raised.
    gone = docs / "features/f/plan/tasks/TASK-0002.md"
    _save(bus, gone, docs, kind="modified")  # file does not exist
    assert [e for e in events if e.event_type == "cockpit:status-change"] == []
