"""A write must be readable by the very next request ([[ISS-0264]]).

The index is refreshed by the WATCHER, which is asynchronous. `mark-check`
answered `ok` in about a millisecond and the index caught up at roughly fifty,
so the renderer — which repaints the moment the POST resolves — always lost
that race. The visible symptom was that the first tick did nothing and the
second showed the first one's result.

**No watcher is running in these tests**, which is what makes them sharp: the
only thing that can make the write visible is the endpoint doing it, so a
regression cannot be masked by a filesystem event arriving in time.
"""

from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path
from typing import Any

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)

CHECK = """---
type: "[[test]]"
id: TST-0001
aliases: ["TST-0001"]
title: "Race Probe"
status: active
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
tier: 1
area: "Monetization"
mark: todo
verdict_date: ""
verdict_reason: ""
invalidated_by: {}
automation: manual
covered_by: []
covers: ["[[FEAT-0001]]"]
evidence: []
related: []
level: acceptance
---

# Race Probe
"""

FEATURE = """---
type: "[[feature]]"
id: FEAT-0001
title: "Thing"
status: done
---

# Thing
"""


def _docs(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "tests" / "acceptance").mkdir(parents=True)
    (docs / "features").mkdir(parents=True)
    (docs / "tests" / "acceptance" / "TST-0001-Race.md").write_text(
        CHECK, encoding="utf-8")
    (docs / "features" / "FEAT-0001-Thing.md").write_text(
        FEATURE, encoding="utf-8")
    return docs


def _spin_up(docs: Path):
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(server.docs_root, server.index, server.bus,
                      cockpit_state=server.cockpit_state),
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd.server_address[1], httpd


def _get(port: int, path: str) -> Any:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
        return json.loads(r.read())


def _post(port: int, path: str, body: dict) -> Any:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=json.dumps(body).encode(),
        method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def _blocking_mark(port: int) -> str:
    rows = (_get(port, "/api/cockpit/acceptance").get("gate") or {}).get("blocking") or []
    return rows[0]["mark"] if rows else "settled"


def test_a_mark_is_visible_to_the_next_read(tmp_path: Path) -> None:
    port, httpd = _spin_up(_docs(tmp_path))
    try:
        assert _blocking_mark(port) == "todo"
        assert _post(port, "/api/notes/mark-check", {
            "id": "TST-0001", "number": "TST-0001", "name": "Race Probe",
            "verdict": "pass", "reason": "", "change": "",
            "by": "user:edwin", "method": "manual"})["ok"] is True
        #: No sleep, no retry, no watcher. The read that follows the write is
        #: the read the renderer issues, and it must not see the old value.
        assert _blocking_mark(port) == "settled", (
            "the mark is not readable by the next request — a walker has to "
            "tick twice before a check disappears (ISS-0264)")
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_the_endpoint_reindexes_before_it_answers() -> None:
    """Order matters and is invisible at runtime: reindexing AFTER the response
    still passes a slow test on a fast machine while losing the race in the
    app, because the client is already fetching."""
    src = (Path(__file__).resolve().parents[1] / "src" / "project_os_cockpit"
           / "server.py").read_text(encoding="utf-8")
    i = src.index("def _serve_mark_check")
    body = src[i:src.index("def _serve_retire_check", i)]
    assert "self._reindex(check_id)" in body, body[-600:]
    assert body.index("self._reindex(check_id)") < body.rindex(
        'self._respond_json({"ok": True'), "reindex must precede the response"
