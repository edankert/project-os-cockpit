"""HTTP-level + SSE tests for the focus / tab-state endpoints
(FEAT-0008 / TASK-0069).

`test_cockpit_state.py` already exercises the `CockpitState` class
directly; this module covers the wire-level contract:

- `POST /api/cockpit/focus`: response shape, target resolution,
  400 on missing target, 404 on unresolvable target, and the
  `cockpit:focus` SSE event that fires after a successful focus.
- `POST /api/cockpit/tab-state`: response shape, 400 on missing
  fields, and the tab snapshot's interaction with the heartbeat.
- `GET /_events`: the `cockpit:focus` and `file-changed` event
  envelopes (verifying clients can parse them).
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

import pytest

from project_os_cockpit.events import FileEvent
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _make_workspace(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text(
        "---\nid: README\ntitle: README\n---\n# README\nbody\n",
        encoding="utf-8",
    )
    return docs


def _spin_up(docs: Path) -> tuple[DocsServer, _NoDNSThreadingHTTPServer, int]:
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
    return server, httpd, port


def _post(port: int, path: str, body: dict[str, Any]) -> tuple[int, dict]:
    url = f"http://127.0.0.1:{port}{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _get_json(port: int, path: str) -> dict:
    url = f"http://127.0.0.1:{port}{path}"
    with urllib.request.urlopen(url, timeout=2) as resp:
        return json.loads(resp.read())


# ---- POST /api/cockpit/focus ----

def test_focus_happy_path_resolves_id(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(port, "/api/cockpit/focus", {"target": "README"})
        assert status == 200
        assert body["ok"] is True
        # `id: README` in the .md frontmatter takes precedence over
        # the top-level support-file lookup, so the resolver returns
        # the indexed docs path.
        assert body["url"] == "/docs/README.md"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_focus_400_on_missing_target(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(port, "/api/cockpit/focus", {})
        assert status == 400
        assert body["ok"] is False
        assert "target" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_focus_404_on_unresolvable_target(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(
            port, "/api/cockpit/focus",
            {"target": "NOT-A-REAL-ID-1234"},
        )
        assert status == 404
        assert body["ok"] is False
        assert "resolve" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_focus_updates_state_snapshot(tmp_path: Path):
    """After a successful focus, GET /api/cockpit/state.agent_focus
    must reflect the most recent target — that's the bi-directional
    awareness contract the `cockpit state` CLI consumes."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _post(port, "/api/cockpit/focus", {"target": "README"})
        snapshot = _get_json(port, "/api/cockpit/state")
        assert snapshot["agent_focus"] is not None
        assert snapshot["agent_focus"]["target"] == "README"
        assert snapshot["agent_focus"]["url"] == "/docs/README.md"
        # History gained one entry from source: 'agent'.
        history = snapshot["history"]
        assert any(
            ev.get("source") == "agent" and ev.get("target") == "README"
            for ev in history
        )
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- POST /api/cockpit/tab-state ----

def test_tab_state_happy_path(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        status, body = _post(
            port, "/api/cockpit/tab-state",
            {"tab_id": "abc-123", "url": "/README.md", "following": True},
        )
        assert status == 200
        assert body == {"ok": True}
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_tab_state_400_on_missing_fields(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        # missing url
        status, body = _post(port, "/api/cockpit/tab-state", {"tab_id": "x"})
        assert status == 400
        assert body["ok"] is False
        # missing tab_id
        status, body = _post(port, "/api/cockpit/tab-state", {"url": "/x"})
        assert status == 400
        assert body["ok"] is False
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_tab_state_appears_in_snapshot(tmp_path: Path):
    """A heartbeat with `following: true` should appear in the
    snapshot's `tabs` list with the correct flag."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        _post(
            port, "/api/cockpit/tab-state",
            {"tab_id": "tab-A", "url": "/docs/README.md", "following": True},
        )
        snapshot = _get_json(port, "/api/cockpit/state")
        tabs = snapshot["tabs"]
        assert len(tabs) == 1
        assert tabs[0]["tab_id"] == "tab-A"
        assert tabs[0]["url"] == "/docs/README.md"
        assert tabs[0]["following"] is True
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- GET /_events (SSE) ----

def _open_sse(port: int) -> tuple[socket.socket, bytes]:
    """Open an SSE connection; return socket + any bytes already in the
    buffer past the HTTP response headers."""
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
    sock: socket.socket,
    body_buffer: bytes,
    event_name: str,
    timeout: float = 3.0,
) -> str | None:
    """Read from the SSE socket until an event with the given name
    arrives; return its data line. Returns None on timeout."""
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


def test_sse_emits_cockpit_focus_event(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs)
    try:
        sock, body_start = _open_sse(port)
        try:
            # Trigger a focus in a separate thread — the main thread
            # is now reading the long-lived SSE response.
            def fire():
                time.sleep(0.1)
                _post(port, "/api/cockpit/focus", {"target": "README"})
            threading.Thread(target=fire, daemon=True).start()
            data = _wait_for_event(sock, body_start, "cockpit:focus")
            assert data is not None, "no cockpit:focus event arrived within 3s"
            payload = json.loads(data)
            assert payload["target"] == "README"
            assert payload["url"] == "/docs/README.md"
        finally:
            sock.close()
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_sse_emits_file_changed_event(tmp_path: Path):
    """Inject a FileEvent on the bus (the same path the file
    watcher uses) and assert the SSE channel surfaces a
    `file-changed` envelope with the rel-path as plain-text data."""
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs)
    try:
        sock, body_start = _open_sse(port)
        try:
            def fire():
                time.sleep(0.1)
                server.bus.publish(FileEvent(
                    kind="modified",
                    rel_path="features/x.md",
                    abs_path=docs / "features" / "x.md",
                ))
            threading.Thread(target=fire, daemon=True).start()
            data = _wait_for_event(sock, body_start, "file-changed")
            assert data is not None, "no file-changed event arrived within 3s"
            assert data == "features/x.md"
        finally:
            sock.close()
    finally:
        httpd.shutdown()
        httpd.server_close()
