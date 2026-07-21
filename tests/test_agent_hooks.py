"""HTTP + tracker tests for hook-fed agent ingestion (FEAT-0019 / TASK-0114).

Covers:
- `POST /api/agent-hook` event → headline-state mapping (busy /
  needs-input / waiting / idle) visible in `/api/cockpit/state`.
- Activity + session blocks in the state snapshot (prompt, tool/file,
  cost via Statusline, undocumented-work rule — TASK-0125).
- Validation: malformed JSON, non-object body, missing
  hook_event_name, unknown-event tolerance, oversized payload.
- Precedence: manual `POST /api/cockpit/agent-state` is superseded
  while a hook session is live.
- SSE `cockpit:agent-activity` delivery.
- `GET /api/cockpit/sessions` (TASK-0123) + persistence seed semantics.
- CHG provenance correlation + `/api/render` enrichment (TASK-0126).
"""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit.agent_hooks import AgentSessionTracker
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _make_workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (docs / "changes").mkdir()
    return docs


def _spin_up(docs: Path, tracker: AgentSessionTracker | None = None):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
            agent_tracker=tracker or server.agent_tracker,
        ),
    )
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return server, httpd, port


def _post(port: int, path: str, body: dict[str, Any] | bytes) -> tuple[int, dict]:
    url = f"http://127.0.0.1:{port}{path}"
    data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _hook(port: int, body: dict[str, Any]) -> tuple[int, dict]:
    return _post(port, "/api/agent-hook", body)


def _get(port: int, path: str) -> dict:
    with urllib.request.urlopen(
        f"http://127.0.0.1:{port}{path}", timeout=3,
    ) as resp:
        return json.loads(resp.read())


SID = "sess-1234"


def _ev(name: str, **fields: Any) -> dict[str, Any]:
    return {"hook_event_name": name, "session_id": SID, **fields}


# ---- headline state mapping ----

def test_prompt_submit_maps_to_busy(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _hook(port, _ev("UserPromptSubmit", prompt="fix the bug"))
        assert (status, body["ok"]) == (200, True)
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "busy"
        assert snap["agent_state"]["source"] == "hook"
        assert snap["activity"]["prompt"] == "fix the bug"
        assert snap["session"]["session_id"] == SID
        assert snap["session"]["live"] is True
        assert snap["session"]["last_prompt"] == "fix the bug"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_permission_and_notification_severity(tmp_path: Path):
    """PermissionRequest and blocking-notification subtypes escalate to
    needs-input; an idle_prompt (turn finished) is only `waiting`, not
    the red blocked tier (TASK-0156)."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _hook(port, _ev("PermissionRequest", tool_name="Bash"))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "needs-input"
        assert "Bash" in snap["agent_state"]["message"]

        # A genuine mid-work block still escalates to needs-input.
        _hook(port, _ev("UserPromptSubmit", prompt="go on"))
        _hook(port, _ev(
            "Notification",
            notification_type="permission_prompt",
            message="approve this edit?",
        ))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "needs-input"

        # idle_prompt (finished turn) must NOT go red — it is waiting.
        _hook(port, _ev(
            "Notification",
            notification_type="idle_prompt",
            message="Claude is waiting for your input",
        ))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "waiting"
        assert "waiting" in snap["agent_state"]["message"].lower()

        # An unrecognised notification subtype changes nothing.
        _hook(port, _ev(
            "Notification", notification_type="progress", message="50%",
        ))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "waiting"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_stop_and_session_end_map_to_waiting_then_idle(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _hook(port, _ev("UserPromptSubmit", prompt="do it"))
        _hook(port, _ev("Stop", message="all done, review please"))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "waiting"

        _hook(port, _ev("SessionEnd", reason="exit"))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "idle"
        assert snap["session"] is None  # ended sessions are not live
        # …but the most-recent session is exposed as last_session so the
        # agent strip keeps showing it (files included) between runs.
        assert snap["last_session"] is not None
        assert snap["last_session"]["session_id"] == SID
        assert snap["last_session"]["live"] is False
        sessions = _get(port, "/api/cockpit/sessions")["sessions"]
        assert sessions[0]["session_id"] == SID
        assert sessions[0]["live"] is False
        assert sessions[0]["prompts"][0]["text"] == "do it"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_normalize_reset_to_iso():
    """resets_at is normalised to an ISO string so every UI surface
    parses it identically (review finding F2)."""
    from project_os_cockpit.agent_hooks import _normalize_reset
    assert _normalize_reset("2026-07-19T14:00:00Z") == "2026-07-19T14:00:00Z"
    # epoch seconds
    iso_s = _normalize_reset(1_784_400_000)
    assert isinstance(iso_s, str) and iso_s.startswith("2026-")
    # epoch milliseconds → same instant
    iso_ms = _normalize_reset(1_784_400_000_000)
    assert iso_ms == iso_s
    assert _normalize_reset(None) is None
    assert _normalize_reset({}) is None


def test_latest_rate_limits_is_freshest_across_sessions(tmp_path: Path):
    """The account-global reading is the newest captured_at across ALL
    sessions — a later session without a reading can't mask an earlier
    one that has it (TASK-0171)."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        # Session A: real reading with a captured_at.
        _hook(port, {"hook_event_name": "UserPromptSubmit",
                     "session_id": "A", "prompt": "a"})
        _hook(port, {"hook_event_name": "Statusline", "session_id": "A",
                     "cost": {"total_cost_usd": 1},
                     "rate_limits": {
                         "five_hour": {"used_percentage": 17},
                         "seven_day": {"used_percentage": 58},
                     }})
        # Session B (later): no rate_limits at all.
        _hook(port, {"hook_event_name": "UserPromptSubmit",
                     "session_id": "B", "prompt": "b"})
        _hook(port, {"hook_event_name": "SessionEnd", "session_id": "B"})
        snap = _get(port, "/api/cockpit/state")
        assert snap.get("rate_limits") is not None
        assert snap["rate_limits"]["five_hour"]["used_percentage"] == 17
        assert snap["rate_limits"]["seven_day"]["used_percentage"] == 58
        assert isinstance(snap.get("rate_limits_at"), str)
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_double_capture_is_deduped(tmp_path: Path):
    """The terminal + external hooks post the same payload ~100ms apart;
    the tracker records it once (TASK-0152). A genuinely different
    payload for the same session still lands."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        ev = _ev("UserPromptSubmit", prompt="build it")
        code1, out1 = _hook(port, ev)
        code2, out2 = _hook(port, dict(ev))  # identical, immediately after
        assert code1 == 200 and code2 == 200
        assert out2.get("ignored") is True and out2.get("duplicate") is True
        sessions = _get(port, "/api/cockpit/sessions")["sessions"]
        assert len(sessions[0]["prompts"]) == 1  # not 2

        # A different prompt is NOT a duplicate.
        _hook(port, _ev("UserPromptSubmit", prompt="now test it"))
        sessions = _get(port, "/api/cockpit/sessions")["sessions"]
        assert len(sessions[0]["prompts"]) == 2
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_last_session_retains_files_after_end(tmp_path: Path):
    """After a session ends, snapshot.last_session still carries the
    files it touched — the data the persistent agent strip renders."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _hook(port, _ev("UserPromptSubmit", prompt="edit things"))
        _hook(port, _ev(
            "PostToolUse", tool_name="Edit",
            tool_input={"file_path": str(docs.parent / "src" / "thing.py")},
        ))
        # While live, session carries the file; last_session is absent.
        snap = _get(port, "/api/cockpit/state")
        assert snap["session"] is not None
        assert any("thing.py" in f for f in snap["session"]["files"])
        assert snap["last_session"] is None

        _hook(port, _ev("SessionEnd", reason="exit"))
        snap = _get(port, "/api/cockpit/state")
        assert snap["session"] is None
        assert snap["last_session"] is not None
        assert any("thing.py" in f for f in snap["last_session"]["files"])
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- tool events, files, undocumented rule ----

def test_tool_events_record_files_and_undocumented_rule(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        src_file = str(tmp_path / "src" / "main.py")
        _hook(port, _ev(
            "PostToolUse", tool_name="Edit",
            tool_input={"file_path": src_file},
        ))
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "busy"
        assert snap["activity"]["file"] == src_file
        assert snap["session"]["undocumented"] is True

        docs_note = str(docs / "changes" / "CHG-20260705-Test.md")
        _hook(port, _ev(
            "PostToolUse", tool_name="Write",
            tool_input={"file_path": docs_note},
        ))
        snap = _get(port, "/api/cockpit/state")
        assert snap["activity"]["rel"] == "changes/CHG-20260705-Test.md"
        assert snap["session"]["undocumented"] is False
        assert "changes/CHG-20260705-Test.md" in snap["session"]["docs_notes"]
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_statusline_updates_cost(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _hook(port, _ev("UserPromptSubmit", prompt="work"))
        status, body = _hook(port, _ev(
            "Statusline",
            cost={"total_cost_usd": 1.25, "total_lines_added": 10},
            context_window={"used_percentage": 42},
        ))
        assert status == 200 and body["ok"] is True
        snap = _get(port, "/api/cockpit/state")
        assert snap["session"]["cost"]["total_cost_usd"] == 1.25
        assert snap["session"]["cost"]["used_percentage"] == 42
        # Statusline never flips the headline state.
        assert snap["agent_state"]["state"] == "busy"
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- validation ----

def test_validation_rejects_bad_payloads(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(port, "/api/agent-hook", b"not json{")
        assert status == 400 and body["ok"] is False

        status, body = _post(port, "/api/agent-hook", b'["a", "list"]')
        assert status == 400 and body["ok"] is False

        status, body = _hook(port, {"session_id": "x"})
        assert status == 400 and "hook_event_name" in body["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_query_param_defaults_for_forwarders(tmp_path: Path):
    """The statusline / Codex notify shell forwarders pass a raw
    upstream blob and set ?event=&agent= — including Codex's
    `thread-id` in place of `session_id`."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(
            port,
            "/api/agent-hook?event=Stop&agent=codex",
            {"thread-id": "codex-th-1", "last-assistant-message": "done!"},
        )
        assert (status, body["ok"]) == (200, True)
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "waiting"
        assert snap["agent_state"]["agent"] == "codex"
        assert snap["session"]["session_id"] == "codex-th-1"
        assert snap["session"]["agent"] == "codex"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_unknown_event_is_accepted_and_ignored(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _hook(port, _ev("FutureFancyEvent", data="whatever"))
        assert status == 200
        assert body == {"ok": True, "ignored": True}
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"] is None  # no state invented
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_oversized_payload_rejected(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        big = json.dumps(
            {"hook_event_name": "UserPromptSubmit", "prompt": "x" * (3 * 1024 * 1024)}
        ).encode("utf-8")
        url = f"http://127.0.0.1:{port}/api/agent-hook"
        req = urllib.request.Request(
            url, data=big, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        except (ConnectionResetError, BrokenPipeError, urllib.error.URLError):
            # Server drops the connection without reading the body —
            # acceptable for an oversized payload.
            status = 413
        assert status == 413
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- precedence ----

def test_manual_signal_superseded_while_hook_session_live(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _hook(port, _ev("UserPromptSubmit", prompt="hook work"))
        status, body = _post(
            port, "/api/cockpit/agent-state", {"state": "done"},
        )
        assert status == 200
        assert body == {"ok": True, "superseded_by_hooks": True}
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "busy"

        # After SessionEnd, manual signalling regains authority.
        _hook(port, _ev("SessionEnd"))
        status, body = _post(
            port, "/api/cockpit/agent-state", {"state": "done"},
        )
        assert status == 200 and body == {"ok": True}
        snap = _get(port, "/api/cockpit/state")
        assert snap["agent_state"]["state"] == "done"
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- SSE activity delivery ----

def _open_sse(port: int) -> tuple[socket.socket, bytes]:
    sock = socket.create_connection(("127.0.0.1", port), timeout=3)
    sock.sendall(
        b"GET /_events HTTP/1.1\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Accept: text/event-stream\r\n"
        b"Connection: keep-alive\r\n"
        b"\r\n"
    )
    sock.settimeout(3)
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise AssertionError("SSE socket closed before headers")
        buf += chunk
    _headers, body_start = buf.split(b"\r\n\r\n", 1)
    return sock, body_start


def _wait_for_event(
    sock: socket.socket, body_buffer: bytes, event_name: str,
    timeout: float = 3.0,
) -> str | None:
    deadline = time.time() + timeout
    buffer = body_buffer
    while time.time() < deadline:
        text = buffer.decode("utf-8", errors="replace")
        marker = f"event: {event_name}\n"
        idx = text.find(marker)
        if idx >= 0:
            after = text[idx + len(marker):]
            for line in after.split("\n"):
                if line.startswith("data: "):
                    return line[len("data: "):]
                if line == "":
                    return ""
        try:
            sock.settimeout(max(0.1, deadline - time.time()))
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        buffer += chunk
    return None


def test_sse_emits_agent_activity_on_hook(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        sock, body_start = _open_sse(port)
        try:
            def fire():
                time.sleep(0.1)
                _hook(port, _ev("UserPromptSubmit", prompt="stream me"))
            threading.Thread(target=fire, daemon=True).start()
            data = _wait_for_event(sock, body_start, "cockpit:agent-activity")
            assert data is not None, "no cockpit:agent-activity event within 3s"
            payload = json.loads(data)
            assert payload["event"] == "UserPromptSubmit"
            assert payload["prompt"] == "stream me"
            assert payload["state"] == "busy"
        finally:
            sock.close()
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- persistence + provenance (tracker-level) ----

def test_session_persistence_and_seed(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    sessions_path = tmp_path / ".cockpit" / "sessions.json"
    tracker = AgentSessionTracker(docs_root=docs, sessions_path=sessions_path)
    tracker.ingest(_ev("SessionStart"))
    tracker.ingest(_ev("UserPromptSubmit", prompt="persist me"))
    tracker.ingest(_ev("SessionEnd"))
    assert sessions_path.is_file()
    data = json.loads(sessions_path.read_text(encoding="utf-8"))
    assert data["sessions"][0]["session_id"] == SID

    # Simulate a crash mid-session: live session on disk gets closed on seed.
    data["sessions"][0]["ended"] = None
    sessions_path.write_text(json.dumps(data), encoding="utf-8")
    tracker2 = AgentSessionTracker(docs_root=docs, sessions_path=sessions_path)
    assert tracker2.has_live_session() is False
    assert tracker2.sessions_payload()[0]["ended"] is not None


def test_seeded_session_revives_on_fresh_activity(tmp_path: Path):
    """ISS-0014 / TASK-0183: the soft live-reload (TASK-0014) restarts the
    sidecar under a still-running terminal, so `_seed` stamps the live
    session `ended`. A subsequent hook from that still-alive session must
    revive it — otherwise its live cost/context never shows in the strip.
    A `SessionEnd` must NOT revive."""
    docs = _make_workspace(tmp_path)
    sessions_path = tmp_path / ".cockpit" / "sessions.json"
    t1 = AgentSessionTracker(docs_root=docs, sessions_path=sessions_path)
    t1.ingest(_ev("SessionStart"))
    t1.ingest(_ev("Statusline",
                  cost={"total_cost_usd": 12.3},
                  context_window={"used_percentage": 40}))
    t1._persist_locked(force=True)
    assert t1.has_live_session() is True

    # Sidecar restarts while the terminal survives → seed marks it ended.
    t2 = AgentSessionTracker(docs_root=docs, sessions_path=sessions_path)
    assert t2.has_live_session() is False

    # The still-alive session posts a fresh statusline (no new SessionStart).
    t2.ingest(_ev("Statusline",
                  cost={"total_cost_usd": 13.4},
                  context_window={"used_percentage": 41}))
    assert t2.has_live_session() is True
    snap = t2.snapshot()
    assert snap.get("session") is not None          # shown as the LIVE session
    cost = snap["session"]["cost"]
    assert cost["total_cost_usd"] == 13.4           # fresh cost surfaced
    assert cost["used_percentage"] == 41            # fresh ctx surfaced

    # A SessionEnd genuinely ends it again.
    t2.ingest(_ev("SessionEnd"))
    assert t2.has_live_session() is False


def test_chg_provenance_via_render(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    chg = docs / "changes" / "CHG-20260705-Shipped.md"
    chg.write_text(
        "---\ntype: \"[[change]]\"\nid: CHG-20260705-Shipped\n---\n\n# Shipped\n",
        encoding="utf-8",
    )
    server, httpd, port = _spin_up(docs)
    tracker = server.agent_tracker
    try:
        _hook(port, _ev("UserPromptSubmit", prompt="ship it"))
        _hook(port, _ev(
            "Statusline", cost={"total_cost_usd": 2.5},
        ))
        tracker.on_file_event("created", "changes/CHG-20260705-Shipped.md")
        payload = _get(
            port, "/api/render?path=changes/CHG-20260705-Shipped.md",
        )
        assert payload["produced_by"]["session_id"] == SID
        assert payload["produced_by"]["total_cost_usd"] == 2.5
        # Undocumented flag is cleared by the CHG association.
        snap = _get(port, "/api/cockpit/state")
        assert snap["session"]["undocumented"] is False
        assert "CHG-20260705-Shipped" in snap["session"]["chg_ids"]
    finally:
        httpd.shutdown()
        httpd.server_close()
