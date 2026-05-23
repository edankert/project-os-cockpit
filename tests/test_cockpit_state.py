"""Unit tests for ``CockpitState`` (TASK-0053).

The class lives in ``project_os_cockpit.server``; we exercise it directly
instead of via HTTP to keep the tests fast and free of port allocation.
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
