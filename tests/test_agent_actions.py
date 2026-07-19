"""Agent verb registry (FEAT-0024 / TASK-0131, TST-0013)."""

from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path

from project_os_cockpit.agent_actions import DEFAULT_ACTIONS, load_actions
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)


def test_defaults_cover_all_dispatchable_types():
    for note_type in ("task", "issue", "feature", "requirement", "phase", "risk"):
        actions = DEFAULT_ACTIONS[note_type]
        assert actions, note_type
        defaults = [a for a in actions if a.get("default")]
        assert len(defaults) == 1, f"{note_type} needs exactly one default"
        for a in actions:
            assert "{id}" in a["prompt"] or "{rel}" in a["prompt"]


def test_yaml_override_replaces_type_wholesale(tmp_path: Path):
    override = tmp_path / "tools" / "adapters" / "cockpit" / "actions.yaml"
    override.parent.mkdir(parents=True)
    override.write_text(
        "task:\n"
        "  - key: yolo\n"
        "    label: Just do it\n"
        "    default: true\n"
        "    prompt: \"Do {id} now, read docs/{rel}\"\n"
        "bogus-entries:\n"
        "  - key: ''\n"
        "    label: broken\n",
        encoding="utf-8",
    )
    actions = load_actions(tmp_path)
    assert [a["key"] for a in actions["task"]] == ["yolo"]
    # Invalid entries dropped; empty result keeps... nothing valid → type absent from override, defaults kept.
    assert "bogus-entries" not in actions
    # Untouched types keep the built-ins.
    assert actions["issue"] == DEFAULT_ACTIONS["issue"]


def test_malformed_yaml_falls_back_to_defaults(tmp_path: Path):
    override = tmp_path / "tools" / "adapters" / "cockpit" / "actions.yaml"
    override.parent.mkdir(parents=True)
    override.write_text("task: [unclosed", encoding="utf-8")
    actions = load_actions(tmp_path)
    assert actions == {k: v for k, v in DEFAULT_ACTIONS.items()}


def test_endpoint_serves_registry(tmp_path: Path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
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
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/cockpit/actions", timeout=3,
        ) as resp:
            body = json.loads(resp.read())
        assert body["actions"]["task"][0]["key"] == "implement"
        assert any(a["key"] == "groom" for a in body["actions"]["phase"])
    finally:
        httpd.shutdown()
        httpd.server_close()
