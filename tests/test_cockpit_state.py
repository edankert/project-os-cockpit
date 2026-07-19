"""Unit tests for ``CockpitState`` (TASK-0053 + TASK-0076).

The class lives in ``project_os_cockpit.server``; we exercise it directly
instead of via HTTP to keep the tests fast and free of port allocation.
TASK-0076 adds the agent-state slice — recording, snapshot inclusion,
lazy decay, and decay-tick semantics.
"""

from __future__ import annotations

import time

import pytest

from project_os_cockpit import server as server_module
from project_os_cockpit.server import CockpitState


def test_initial_snapshot_is_empty():
    state = CockpitState()
    snap = state.snapshot()
    assert snap["agent_focus"] is None
    assert snap["user_view"] is None
    assert snap["tabs"] == []
    assert snap["history"] == []


def test_agent_focus_recorded_in_focus_and_history():
    state = CockpitState()
    state.record_agent_focus("TASK-0053", "/docs/x.md")
    snap = state.snapshot()
    assert snap["agent_focus"]["target"] == "TASK-0053"
    assert snap["agent_focus"]["url"] == "/docs/x.md"
    assert snap["history"][0]["source"] == "agent"
    assert snap["history"][0]["target"] == "TASK-0053"


def test_tab_update_creates_history_only_on_url_change():
    state = CockpitState()
    state.update_tab("t1", "/docs/a.md", True)
    state.update_tab("t1", "/docs/a.md", True)  # heartbeat — same URL
    state.update_tab("t1", "/docs/b.md", True)  # nav
    history = state.snapshot()["history"]
    sources = [h["source"] for h in history]
    assert sources.count("user") == 2  # initial + nav, no heartbeat noise


def test_user_view_picks_most_recent_tab():
    state = CockpitState()
    state.update_tab("old", "/docs/old.md", True)
    time.sleep(0.01)
    state.update_tab("new", "/docs/new.md", True)
    assert state.snapshot()["user_view"]["url"] == "/docs/new.md"


def test_stale_tabs_pruned(monkeypatch):
    state = CockpitState()
    state.update_tab("t1", "/docs/a.md", True)
    # Fast-forward beyond the stale threshold.
    monkeypatch.setattr(
        server_module, "_TAB_STALE_SECONDS", -1
    )
    # The pruning happens inside snapshot() — force the cutoff to a
    # value that excludes any timestamp.
    snap = state.snapshot()
    assert snap["tabs"] == []
    assert snap["user_view"] is None


def test_history_is_bounded():
    state = CockpitState()
    for i in range(server_module._HISTORY_MAX + 25):
        state.update_tab(f"t{i}", f"/docs/{i}.md", True)
    assert len(state.snapshot()["history"]) == server_module._HISTORY_MAX


def test_following_flag_round_trips():
    state = CockpitState()
    state.update_tab("t1", "/docs/a.md", False)
    snap = state.snapshot()
    assert snap["tabs"][0]["following"] is False
    state.update_tab("t1", "/docs/a.md", True)
    snap = state.snapshot()
    assert snap["tabs"][0]["following"] is True


# ----------------------------------------------------------------------
# FEAT-0013 / TASK-0076 — agent_state slice
# ----------------------------------------------------------------------

def test_agent_state_initially_none():
    state = CockpitState()
    assert state.snapshot()["agent_state"] is None


def test_record_agent_state_basic():
    state = CockpitState()
    payload = state.record_agent_state("busy", target="FEAT-0013", agent="claude")
    # Method returns the canonical payload so the caller can fan it
    # out as an SSE event without re-reading the snapshot.
    assert payload["state"] == "busy"
    assert payload["target"] == "FEAT-0013"
    assert payload["agent"] == "claude"
    assert "ts" in payload
    snap = state.snapshot()
    assert snap["agent_state"] == payload


def test_record_agent_state_optional_fields_elided():
    state = CockpitState()
    payload = state.record_agent_state("done")
    assert payload == {"state": "done", "ts": payload["ts"]}
    # Keys for unsupplied optional fields must NOT appear.
    assert "target" not in payload
    assert "agent" not in payload
    assert "message" not in payload


def test_agent_state_pushes_to_history():
    state = CockpitState()
    state.record_agent_state("waiting", message="review my PR")
    history = state.snapshot()["history"]
    assert history[0]["source"] == "agent-state"
    assert history[0]["state"] == "waiting"
    assert history[0]["message"] == "review my PR"


def test_lazy_decay_flips_busy_to_idle_after_window(monkeypatch):
    state = CockpitState()
    # Shrink the decay window so the test doesn't sleep for 10 min.
    monkeypatch.setattr(server_module, "_AGENT_STATE_DECAY_SECONDS", 0)
    state.record_agent_state("busy", target="FEAT-0013")
    time.sleep(0.01)
    eff = state.snapshot()["agent_state"]
    assert eff["state"] == "idle"
    assert eff["decayed_from"] == "busy"


def test_lazy_decay_does_not_touch_done_or_error(monkeypatch):
    """`done` and `error` are explicit terminal states — they should
    survive the decay window unchanged, not get flipped to idle."""
    monkeypatch.setattr(server_module, "_AGENT_STATE_DECAY_SECONDS", 0)
    state = CockpitState()
    state.record_agent_state("done")
    time.sleep(0.01)
    assert state.snapshot()["agent_state"]["state"] == "done"


def test_lazy_decay_preserves_stored_value(monkeypatch):
    """Snapshot reports `idle` but the stored value stays — a fresh
    `record_agent_state` clears the decay-observed flag so a
    subsequent decay can fire its own SSE."""
    monkeypatch.setattr(server_module, "_AGENT_STATE_DECAY_SECONDS", 0)
    state = CockpitState()
    state.record_agent_state("busy")
    time.sleep(0.01)
    state.snapshot()  # observation only — should not mutate stored
    # decay_tick (TASK-0077) emits exactly one synthetic event.
    first = state.decay_tick()
    assert first is not None and first["state"] == "idle"
    second = state.decay_tick()
    assert second is None, "decay_tick must be idempotent until next record"


def test_state_file_written_on_record(tmp_path):
    """TASK-0081 — record_agent_state mirrors to disk so cross-
    workspace readers can poll without a live SSE subscription."""
    state_path = tmp_path / ".cockpit" / "agent-state.json"
    state = CockpitState(state_path=state_path)
    state.record_agent_state("busy", target="FEAT-0010", agent="claude")
    import json as _json
    on_disk = _json.loads(state_path.read_text(encoding="utf-8"))
    assert on_disk["state"] == "busy"
    assert on_disk["target"] == "FEAT-0010"
    assert on_disk["agent"] == "claude"


def test_state_file_rewritten_on_decay(tmp_path, monkeypatch):
    monkeypatch.setattr(server_module, "_AGENT_STATE_DECAY_SECONDS", 0)
    state_path = tmp_path / ".cockpit" / "agent-state.json"
    state = CockpitState(state_path=state_path)
    state.record_agent_state("busy")
    time.sleep(0.01)
    payload = state.decay_tick()
    assert payload is not None and payload["state"] == "idle"
    import json as _json
    on_disk = _json.loads(state_path.read_text(encoding="utf-8"))
    assert on_disk["state"] == "idle"
    assert on_disk["decayed_from"] == "busy"


def test_state_file_seeds_on_construction(tmp_path):
    """Restart scenario — a CockpitState constructed with an existing
    state file pre-populates `agent_state` so the rail dot doesn't
    blink off on cockpit restart."""
    import datetime as _dt
    import json as _json
    state_path = tmp_path / ".cockpit" / "agent-state.json"
    state_path.parent.mkdir()
    # A fresh timestamp — a hardcoded past date would (correctly) read
    # back as decayed-to-idle once older than the decay window.
    fresh_ts = _dt.datetime.now(_dt.timezone.utc).isoformat(
        timespec="milliseconds"
    )
    state_path.write_text(_json.dumps({
        "state": "waiting",
        "target": "FEAT-0010",
        "message": "review my PR",
        "ts": fresh_ts,
    }), encoding="utf-8")
    state = CockpitState(state_path=state_path)
    snap = state.snapshot()
    assert snap["agent_state"] is not None
    assert snap["agent_state"]["state"] == "waiting"
    assert snap["agent_state"]["target"] == "FEAT-0010"


def test_state_file_tolerates_missing_and_malformed(tmp_path):
    missing = tmp_path / ".cockpit" / "missing.json"
    state = CockpitState(state_path=missing)
    assert state.snapshot()["agent_state"] is None
    garbled = tmp_path / "junk.json"
    garbled.write_text("not json", encoding="utf-8")
    state2 = CockpitState(state_path=garbled)
    assert state2.snapshot()["agent_state"] is None


def test_record_agent_state_resets_decay_observed(monkeypatch):
    monkeypatch.setattr(server_module, "_AGENT_STATE_DECAY_SECONDS", 0)
    state = CockpitState()
    state.record_agent_state("busy")
    time.sleep(0.01)
    assert state.decay_tick() is not None
    assert state.decay_tick() is None
    # Fresh declaration must unlatch the flag so a NEW decay observable.
    state.record_agent_state("busy")
    time.sleep(0.01)
    assert state.decay_tick() is not None


def test_unknown_post_drains_body_to_keep_connection_synced(tmp_path):
    """Regression: POST to an unknown route on the cockpit used to leave
    the request body in the socket buffer, desyncing HTTP/1.1
    keep-alive — the next request on the same TCP connection got its
    request line prefixed by leftover JSON and the server rejected it
    as ``501 Unsupported method``. Real-world symptom: a fresh static
    asset GET (CSS/JS/favicon) on a connection reused after the bad
    POST fails with 501, leaving the page unstyled.

    We exercise the fix end-to-end against a real ``ThreadingHTTPServer``
    bound to an ephemeral port, sending two pipelined requests on a
    single keep-alive socket.
    """
    import socket
    import threading

    from project_os_cockpit.server import DocsServer, _NoDNSThreadingHTTPServer, _make_handler

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# hi\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
        ),
    )
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=2)
        sock.settimeout(2)
        body = b'{"tab_id":"x","url":"/","following":true}'
        request = (
            b"POST /api/cockpit/does-not-exist HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n"
            b"Connection: keep-alive\r\n"
            b"\r\n" + body +
            b"GET /_static/cockpit.css HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        )
        sock.sendall(request)
        chunks = []
        while True:
            try:
                buf = sock.recv(8192)
            except socket.timeout:
                break
            if not buf:
                break
            chunks.append(buf)
        sock.close()
        raw = b"".join(chunks)
        # Two responses on one TCP connection. First is the 404; second
        # MUST be a 200 with CSS — not a 501 caused by undrained body.
        assert raw.count(b"HTTP/1.1 ") >= 2, raw
        assert b"HTTP/1.1 404" in raw, raw
        assert b"HTTP/1.1 200" in raw, raw
        assert b"Unsupported method" not in raw, raw
    finally:
        httpd.shutdown()
        httpd.server_close()
