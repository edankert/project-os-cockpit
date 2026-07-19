"""Dispatch ledger + requests + status-aware verbs (FEAT-0025/0026, TST-0014)."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit import cli as cli_module
from project_os_cockpit.agent_actions import DEFAULT_ACTIONS, load_actions
from project_os_cockpit.agent_hooks import AgentSessionTracker
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _make_workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "tasks").mkdir(parents=True)
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (docs / "tasks" / "TASK-0001-Demo.md").write_text(
        "---\ntype: \"[[task]]\"\nid: TASK-0001\nstatus: doing\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    return docs


def _spin_up(docs: Path):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
            agent_tracker=server.agent_tracker,
        ),
    )
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return server, httpd, port


def _post(port: int, path: str, body: dict[str, Any]) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _get(port: int, path: str) -> dict:
    with urllib.request.urlopen(
        f"http://127.0.0.1:{port}{path}", timeout=3,
    ) as resp:
        return json.loads(resp.read())


# ---- ledger: stamping + history ----

def test_dispatch_stamps_next_session(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=_make_workspace(tmp_path))
    tracker.record_dispatch("TASK-0001", verb="refine", agent="claude")
    # Pending: history knows it but has no session yet.
    hist = tracker.dispatch_history("TASK-0001")
    assert hist == [{
        "id": "TASK-0001", "ts": hist[0]["ts"], "verb": "refine",
        "agent": "claude", "session_id": None, "live": False, "pending": True,
    }]
    # A session starts → the dispatch is stamped onto it.
    tracker.ingest({"hook_event_name": "UserPromptSubmit",
                    "session_id": "s1", "prompt": "Refine TASK-0001…"})
    hist = tracker.dispatch_history("TASK-0001")
    assert hist[0]["session_id"] == "s1"
    assert hist[0]["live"] is True
    assert not hist[0].get("pending")
    # And the session's slim record carries it.
    sessions = tracker.sessions_payload()
    assert sessions[0]["dispatches"][0]["verb"] == "refine"


def test_dispatch_during_live_session_attaches_to_it(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=_make_workspace(tmp_path))
    tracker.ingest({"hook_event_name": "UserPromptSubmit",
                    "session_id": "s1", "prompt": "working"})
    tracker.record_dispatch("ISS-0002", verb="fix")
    hist = tracker.dispatch_history("ISS-0002")
    assert hist[0]["session_id"] == "s1"


# ---- endpoints ----

def test_dispatch_endpoint_and_requests_handoff(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(port, "/api/cockpit/dispatch",
                             {"id": "task-0001", "verb": "refine",
                              "agent": "claude", "enqueue": True})
        assert status == 200 and body["ok"] is True
        assert body["recorded"]["id"] == "TASK-0001"  # normalised

        status, body = _post(port, "/api/cockpit/dispatch", {})
        assert status == 400

        # Requests hand off exactly once.
        reqs = _get(port, "/api/cockpit/dispatch-requests")["requests"]
        assert [r["id"] for r in reqs] == ["TASK-0001"]
        assert _get(port, "/api/cockpit/dispatch-requests")["requests"] == []
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_render_carries_dispatch_history(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _post(port, "/api/cockpit/dispatch", {"id": "TASK-0001", "verb": "implement"})
        payload = _get(port, "/api/render?path=tasks/TASK-0001-Demo.md")
        assert payload["dispatch_history"][0]["verb"] == "implement"
        # Undispatched notes carry no key at all.
        payload = _get(port, "/api/render?path=README.md")
        assert "dispatch_history" not in payload
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- status-aware verbs (FEAT-0026 / TASK-0137) ----

def test_default_when_lists_encode_lifecycle():
    task = {a["key"]: a for a in DEFAULT_ACTIONS["task"]}
    assert "done" not in task["implement"]["when"]
    assert "backlog" not in task["close-out"]["when"]
    # Entries without `when` are always-on (requirement.verify).
    req = {a["key"]: a for a in DEFAULT_ACTIONS["requirement"]}
    assert "when" not in req["verify"]


def test_yaml_when_passthrough(tmp_path: Path):
    override = tmp_path / "tools" / "adapters" / "cockpit" / "actions.yaml"
    override.parent.mkdir(parents=True)
    override.write_text(
        "adr:\n"
        "  - key: revisit\n"
        "    label: Revisit\n"
        "    prompt: \"Revisit {id} in docs/{rel}\"\n"
        "    when: [Accepted, PROPOSED]\n",
        encoding="utf-8",
    )
    actions = load_actions(tmp_path)
    assert actions["adr"][0]["when"] == ["accepted", "proposed"]


# ---- CLI (TASK-0136) ----

def test_cli_dispatch_posts_enqueue(monkeypatch, capsys):
    calls: list[tuple[str, str, dict]] = []

    def fake_post(base: str, path: str, body: dict) -> tuple[int, dict]:
        calls.append((base, path, body))
        return 200, {"ok": True, "recorded": {"id": "TASK-0001"}}

    monkeypatch.setattr(cli_module, "_post_json", fake_post)
    monkeypatch.setattr(cli_module, "_default_base_url",
                        lambda: "http://127.0.0.1:8765")
    exit_code = cli_module.main(
        ["dispatch", "TASK-0001", "--verb", "refine", "--agent", "claude"],
    )
    assert exit_code == 0
    assert calls == [(
        "http://127.0.0.1:8765",
        "/api/cockpit/dispatch",
        {"id": "TASK-0001", "enqueue": True, "verb": "refine", "agent": "claude"},
    )]
    assert "queued refine for TASK-0001" in capsys.readouterr().out
