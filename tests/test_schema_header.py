"""Every JSON endpoint emits ``X-Cockpit-Schema`` matching the
``cockpit.SCHEMA_VERSION`` constant (FEAT-0008 / TASK-0068).

This is the gate that catches schema drift: if anyone adds a new
JSON endpoint with a hand-rolled response writer that skips the
header, or changes the constant without updating clients, this
test fails on every JSON endpoint and the breakage is loud.

The mode-1 cockpit JS and the mode-3 desktop renderer both cache
the schema version they were built against; the header is how the
server tells them whether they're still in agreement. Without
this test, we'd find out about a missing header from a confused
user, not from CI.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from project_os_cockpit import cockpit
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


def _spin_up(docs: Path) -> tuple[int, _NoDNSThreadingHTTPServer]:
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
    return port, httpd


def _request(
    port: int,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, str]]:
    url = f"http://127.0.0.1:{port}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status, {k: v for k, v in resp.getheaders()}
    except urllib.error.HTTPError as exc:
        return exc.code, {k: v for k, v in exc.headers.items()}


# Tuples of (method, path-with-query, body) — one per JSON endpoint
# documented in docs/references/COCKPIT-API.md. Status code expected
# (so we can include both happy-path and error-shape responses; both
# should still emit X-Cockpit-Schema).
ENDPOINTS: list[tuple[str, str, dict[str, Any] | None, int]] = [
    ("GET",  "/healthz",                                None, 200),
    ("GET",  "/api/cockpit/nav",                        None, 200),
    ("GET",  "/api/cockpit/nav?mode=tasks",             None, 200),
    ("GET",  "/api/cockpit/nav?mode=library",           None, 200),
    ("GET",  "/api/cockpit/context",                    None, 200),
    ("GET",  "/api/cockpit/context?this=README",        None, 200),
    ("GET",  "/api/cockpit/state",                      None, 200),
    ("GET",  "/api/cockpit/validation",                 None, 200),
    ("GET",  "/api/terminal",                           None, 200),
    ("GET",  "/api/render?path=README.md",              None, 200),
    # Error responses must also carry the header — the renderer
    # branches on the schema version before parsing the body.
    ("GET",  "/api/render",                             None, 400),
    ("GET",  "/api/render?path=../escape.md",           None, 403),
    ("GET",  "/api/render?path=missing.md",             None, 404),
    ("POST", "/api/cockpit/focus",                      {"target": "README"}, 200),
    ("POST", "/api/cockpit/focus",                      {}, 400),
    ("POST", "/api/cockpit/tab-state",                  {"tab_id": "t1", "url": "/", "following": True}, 200),
    ("POST", "/api/cockpit/tab-state",                  {}, 400),
]


@pytest.mark.parametrize("method,path,body,expected_status", ENDPOINTS)
def test_schema_header_present(
    tmp_path: Path,
    method: str,
    path: str,
    body: dict[str, Any] | None,
    expected_status: int,
) -> None:
    docs = _make_workspace(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        status, headers = _request(port, method, path, body)
        assert status == expected_status, f"{method} {path} → {status}"
        assert "X-Cockpit-Schema" in headers, (
            f"{method} {path} missing X-Cockpit-Schema "
            f"(schema-versioning rule, COCKPIT-API.md)"
        )
        assert headers["X-Cockpit-Schema"] == str(cockpit.SCHEMA_VERSION), (
            f"{method} {path} header mismatch: "
            f"got {headers['X-Cockpit-Schema']!r}, "
            f"expected {cockpit.SCHEMA_VERSION!r}"
        )
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_healthz_body_schema_matches_header(tmp_path: Path) -> None:
    """`/healthz` returns the schema in both its body (`schema` key)
    and its header. They must agree — drift between the two would
    break the desktop sidecar's identity check."""
    docs = _make_workspace(tmp_path)
    port, httpd = _spin_up(docs)
    try:
        url = f"http://127.0.0.1:{port}/healthz"
        with urllib.request.urlopen(url, timeout=2) as resp:
            headers = {k: v for k, v in resp.getheaders()}
            payload = json.loads(resp.read())
        assert headers["X-Cockpit-Schema"] == str(payload["schema"])
        assert payload["schema"] == cockpit.SCHEMA_VERSION
    finally:
        httpd.shutdown()
        httpd.server_close()
