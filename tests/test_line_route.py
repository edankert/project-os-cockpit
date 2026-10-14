"""`GET /api/cockpit/line`: the cockpit's half of the project line above the
Claude prompt, in one answer (FEAT-0157 / TASK-0672).

The plugin draws this project's needs-you count from it, and the Open in
cockpit button's target. Each test here fails when one promise breaks: the
count differs from the badges', a request from another machine is answered,
an empty focus names a target, or a failure is answered as a zero.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

from project_os_cockpit import cockpit

from test_agent_hooks import _get, _make_workspace, _spin_up


def _note(path: Path, note_type: str, note_id: str, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\ntype: "[[{note_type}]]"\nid: {note_id}\ntitle: "{note_id}"\nstatus: {status}\n---\n\n# {note_id}\n',
        encoding="utf-8",
    )


def _workspace(tmp_path: Path, focus: str = "") -> Path:
    """Three owed notes: two issues to triage and one requirement to approve."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    docs = _make_workspace(tmp_path)
    _note(docs / "issues" / "ISS-0001-a.md", "issue", "ISS-0001", "triage")
    _note(docs / "issues" / "ISS-0002-b.md", "issue", "ISS-0002", "triage")
    _note(docs / "requirements" / "REQ-0001-c.md", "requirement", "REQ-0001", "proposed")
    (tmp_path / "SNAPSHOT.yaml").write_text(f"version: 1\nfocus:\n{focus}  note: \"\"\n", encoding="utf-8")
    return docs


def _status(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=3) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_the_total_is_the_badges_total_and_the_kinds_name_their_verb(tmp_path: Path) -> None:
    docs = _workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        line = _get(port, "/api/cockpit/line")
        badges = _get(port, "/api/cockpit/obligations")
        assert line["schema_version"] == 1
        assert line["needs_you"]["total"] == badges["total"]
        assert line["needs_you"]["total"] >= 3, "the three owed notes are counted"
        kinds = {k["kind"]: k for k in line["needs_you"]["kinds"]}
        assert kinds["issue"] == {"kind": "issue", "count": 2, "verb": "Triage", "noun": "issues"}
        assert kinds["requirement"] == {"kind": "requirement", "count": 1, "verb": "Approve", "noun": "requirement"}
        assert sum(k["count"] for k in line["needs_you"]["kinds"]) == line["needs_you"]["total"]
    finally:
        httpd.shutdown()


def test_the_target_is_the_most_specific_focus_item_and_none_without_focus(tmp_path: Path) -> None:
    docs = _workspace(tmp_path, focus='  task: ""\n  issue: ""\n  feature: "FEAT-0003"\n  phase: "PHASE-001"\n')
    _server, httpd, port = _spin_up(docs)
    try:
        assert _get(port, "/api/cockpit/line")["open_target"] == "FEAT-0003"
    finally:
        httpd.shutdown()

    docs = _workspace(tmp_path / "two", focus='  task: "TASK-0009"\n  feature: "FEAT-0003"\n')
    _server, httpd, port = _spin_up(docs)
    try:
        assert _get(port, "/api/cockpit/line")["open_target"] == "TASK-0009"
    finally:
        httpd.shutdown()

    docs = _workspace(tmp_path / "three", focus='  task: ""\n  feature: ""\n')
    _server, httpd, port = _spin_up(docs)
    try:
        assert _get(port, "/api/cockpit/line")["open_target"] is None
    finally:
        httpd.shutdown()


def test_another_machine_is_refused(tmp_path: Path) -> None:
    docs = _workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    handler_cls = httpd.RequestHandlerClass
    original = handler_cls._is_loopback
    try:
        handler_cls._is_loopback = lambda self: False  # type: ignore[assignment]
        status, body = _status(port, "/api/cockpit/line")
        assert status == HTTPStatus.FORBIDDEN, body
        assert "needs_you" not in body
    finally:
        handler_cls._is_loopback = original  # type: ignore[assignment]
        httpd.shutdown()


def test_a_failure_is_a_500_and_never_a_zero(tmp_path: Path, monkeypatch) -> None:
    docs = _workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)

    def broken(index):
        raise RuntimeError("the registry is unreadable")

    monkeypatch.setattr(cockpit._obligations, "badges_payload", broken)
    try:
        status, body = _status(port, "/api/cockpit/line")
        assert status == HTTPStatus.INTERNAL_SERVER_ERROR
        assert body["ok"] is False and "needs_you" not in body
    finally:
        httpd.shutdown()
