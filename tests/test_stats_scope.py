"""Scoped stats payload + cache (FEAT-0023 / TASK-0128, TST-0012).

Fixture tree: two phases, features/tasks split across them, a test
linked to a scoped feature via `features:`, and exit criteria in the
phase note body.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

from project_os_cockpit import cockpit
from project_os_cockpit.index import Index
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def _note(path: Path, fm: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}: {json.dumps(v)}")
        else:
            lines.append(f'{k}: "{v}"' if isinstance(v, str) and not v.startswith("[[") else f'{k}: {json.dumps(v)}')
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body, encoding="utf-8")


def _make_tree(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    _note(docs / "phases" / "PHASE-001-Alpha.md", {
        "type": "[[phase]]", "id": "PHASE-001", "title": "Alpha",
        "status": "done", "order": 1,
    })
    _note(docs / "phases" / "PHASE-002-Beta.md", {
        "type": "[[phase]]", "id": "PHASE-002", "title": "Beta",
        "status": "active", "order": 2,
    }, body=(
        "# Beta\n\n## Exit Criteria\n"
        "- [x] first criterion met\n"
        "- [ ] second criterion pending\n"
        "## Notes\n- [ ] not an exit criterion\n"
    ))
    _note(docs / "features" / "a" / "FEAT-0001-A.md", {
        "type": "[[feature]]", "id": "FEAT-0001", "title": "Feat A",
        "status": "done", "phase": "[[PHASE-001]]",
    })
    _note(docs / "features" / "b" / "FEAT-0002-B.md", {
        "type": "[[feature]]", "id": "FEAT-0002", "title": "Feat B",
        "status": "in-progress", "phase": "[[PHASE-002]]",
    })
    # Task inherits phase from parent feature (no direct phase).
    _note(docs / "features" / "b" / "plan" / "tasks" / "TASK-0001-B1.md", {
        "type": "[[task]]", "id": "TASK-0001", "title": "B task",
        "status": "done", "parent": "[[FEAT-0002]]",
    })
    _note(docs / "features" / "a" / "plan" / "tasks" / "TASK-0002-A1.md", {
        "type": "[[task]]", "id": "TASK-0002", "title": "A task",
        "status": "done", "parent": "[[FEAT-0001]]",
    })
    # Test linked to the Beta feature only via `features:`.
    _note(docs / "tests" / "TST-0001-B.md", {
        "type": "[[test]]", "id": "TST-0001", "title": "B test",
        "status": "passing", "features": ["[[FEAT-0002]]"],
    })
    return docs


def test_scoped_payload_filters_and_enriches(tmp_path: Path):
    docs = _make_tree(tmp_path)
    index = Index.build(docs)

    full = cockpit.stats_payload(index)
    assert full["scope"] is None
    assert full["hero"]["tasks"]["total"] == 2
    assert len(full["phases"]) == 2

    scoped = cockpit.stats_payload(index, scope="PHASE-002")
    assert scoped is not None
    assert scoped["scope"]["id"] == "PHASE-002"
    assert scoped["scope"]["title"] == "Beta"
    # Only Beta's feature/task/test survive the filter.
    assert scoped["hero"]["features"]["total"] == 1
    assert scoped["hero"]["tasks"]["total"] == 1
    assert scoped["hero"]["tests"] == {"total": 1, "passing": 1}
    assert len(scoped["phases"]) == 1
    assert scoped["phases"][0]["key"] == "PHASE-002"
    assert scoped["phases"][0]["features"][0]["id"] == "FEAT-0002"
    # Exit criteria parsed from the note body, Notes section excluded.
    assert scoped["exit_criteria"] == [
        {"text": "first criterion met", "done": True},
        {"text": "second criterion pending", "done": False},
    ]
    # Scoped recent feed only contains Beta items.
    ids = {r["id"] for r in scoped["activity"]["recent"]}
    assert "TASK-0002" not in ids
    assert "FEAT-0001" not in ids


def test_unknown_scope_returns_none(tmp_path: Path):
    docs = _make_tree(tmp_path)
    index = Index.build(docs)
    assert cockpit.stats_payload(index, scope="PHASE-099") is None


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


def _get(port: int, path: str):
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}{path}", timeout=3,
        ) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_endpoint_scope_and_cache(tmp_path: Path):
    docs = _make_tree(tmp_path)
    server, httpd, port = _spin_up(docs)
    try:
        status, body = _get(port, "/api/cockpit/stats?scope=PHASE-002")
        assert status == 200
        assert body["scope"]["id"] == "PHASE-002"

        status, _ = _get(port, "/api/cockpit/stats?scope=PHASE-042")
        assert status == 404

        # Cache validity: same generation → identical payload identity
        # can't be observed over HTTP, so prove behaviour instead —
        # a stale cache would miss the new task after invalidation.
        new_task = docs / "features" / "b" / "plan" / "tasks" / "TASK-0003-B2.md"
        _note(new_task, {
            "type": "[[task]]", "id": "TASK-0003", "title": "B task 2",
            "status": "backlog", "parent": "[[FEAT-0002]]",
        })
        _, before = _get(port, "/api/cockpit/stats?scope=PHASE-002")
        assert before["hero"]["tasks"]["total"] == 1  # cache still serving
        server.index.invalidate(new_task)             # watcher-equivalent
        _, after = _get(port, "/api/cockpit/stats?scope=PHASE-002")
        assert after["hero"]["tasks"]["total"] == 2   # generation bumped
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_generation_increments_on_invalidate(tmp_path: Path):
    docs = _make_tree(tmp_path)
    index = Index.build(docs)
    g0 = index.generation
    target = docs / "features" / "a" / "FEAT-0001-A.md"
    index.invalidate(target)
    assert index.generation == g0 + 1
