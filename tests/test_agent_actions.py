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


def test_review_desk_verbs_are_registered(tmp_path: Path):
    """The desk's round-trip verbs live in the same registry as every
    other verb (FEAT-0041 / TASK-0208) — it adds a destination for agent
    work, not a parallel mechanism. `revise` and `answer` are dispatched
    by the desk itself rather than from a note menu, so they are asserted
    on the ledger side in test_dispatch_ledger.py; `request-review` is
    the note-menu half and belongs here.
    """
    feature_verbs = {a["key"]: a for a in DEFAULT_ACTIONS["feature"]}
    assert "request-review" in feature_verbs
    review = feature_verbs["request-review"]
    # It must not be the default: proposing review is a deliberate act,
    # and making it the ▶ button would put it in front of "break down".
    assert not review.get("default")
    assert "review-request" in review["prompt"]
    assert "{id}" in review["prompt"]
    # Exactly one default survives the addition.
    assert len([a for a in DEFAULT_ACTIONS["feature"] if a.get("default")]) == 1


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
