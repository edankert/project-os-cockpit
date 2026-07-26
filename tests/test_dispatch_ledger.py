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

    # Requirement verbs are status-gated too (ISS-0028). This assertion used to
    # read `assert "when" not in req["verify"]`, documenting the requirement
    # block as always-on -- which meant an `implemented` requirement still
    # offered "Implement", and the defect was pinned in place by a test.
    req = {a["key"]: a for a in DEFAULT_ACTIONS["requirement"]}
    assert all("when" in a for a in DEFAULT_ACTIONS["requirement"]), \
        "every requirement verb is gated by status"
    assert "implemented" not in req["implement"]["when"]
    assert req["reconcile"]["when"] == ["implemented", "approved"]
    assert req["verify"]["when"] == ["implemented"]


def test_requirement_verbs_do_not_test_gate():
    """ADR-0007: requirements are gated on acceptance criteria, never on tests.

    The `verify` prompt used to say "ensure TST notes exist covering each
    acceptance criterion, run them, and update the requirement's status
    accordingly" -- the requirement-level test gate that ADR retired and the
    validator exempts requirements from. It survived in this surface after
    ISS-0006 swept the instruction files, which is what a fourth copy of a rule
    does. Guard it here so prose cannot drift back.
    """
    for action in DEFAULT_ACTIONS["requirement"]:
        prompt = action["prompt"].lower()
        assert not ("run them" in prompt and "tst" in prompt), (
            f"requirement verb {action['key']!r} instructs running tests to set "
            "a requirement's status; ADR-0007 forbids test-gating requirements"
        )


def test_requirement_has_a_review_path():
    """A requirement must be able to reach the review desk (ISS-0028).

    `feature` has had `request-review` since FEAT-0041; `requirement` had none,
    so the 120 requirements with unresolved acceptance criteria in your-trainer
    were visible in the cockpit with no verb that acted on them.
    """
    req = {a["key"]: a for a in DEFAULT_ACTIONS["requirement"]}
    assert "request-review" in req
    assert "review-request" in req["request-review"]["prompt"]
    assert "reconcile" in req, "the REQ-BOXES workflow needs a verb"


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


def test_review_round_trip_verbs_reach_the_ledger(tmp_path: Path) -> None:
    """The desk's two round-trip legs are ordinary ledger entries.

    `revise` (request-changes) and `answer` (a question reply) ride the
    FEAT-0025 runtime rather than a private channel — TASK-0208's whole
    claim is that the desk adds a *destination*, not a mechanism. If
    these stopped landing in the ledger, the proposal view's provenance
    line would quietly go blank.
    """
    from project_os_cockpit.agent_hooks import AgentSessionTracker

    from project_os_cockpit.review import ReviewStore

    tracker = AgentSessionTracker(docs_root=tmp_path / "docs")
    store = ReviewStore(tmp_path)

    # Leg 1 — the agent files a request; the desk records a ledger entry
    # per item so the proposal view can show provenance.
    request = store.add(
        "review", items=["FEAT-0040", "TASK-0199"], title="Overview rework",
        session_id="7c31", agent="claude",
    )
    for note_id in request["items"]:
        tracker.record_dispatch(note_id, verb="review:review")

    pending = tracker.take_dispatch_requests()
    assert pending == [], "filing a review must not enqueue a CLI request"

    # Leg 2 — the human's reply dispatches back. The ledger must carry
    # both legs against the same item, in order, so "← revise FEAT-0040"
    # can be rendered on the session row.
    tracker.record_dispatch("FEAT-0040", verb="revise", agent="claude")
    tracker.record_dispatch("FEAT-0040", verb="answer", agent="claude")

    session = tracker.snapshot().get("session") or tracker.snapshot().get("last_session")
    entries = (session or {}).get("dispatches") or []
    if not entries:                      # no live session: pending buffer
        entries = [dict(d) for d in tracker._pending_dispatches]  # noqa: SLF001
    verbs = [e["verb"] for e in entries if e["id"] == "FEAT-0040"]
    assert verbs == ["review:review", "revise", "answer"], verbs
    assert all(e["ts"] for e in entries)

    # The request itself is resolvable and its outcome is counted — the
    # measurement ADR-0007's advisory phase depends on.
    store.resolve(request["request_id"], "changes-requested")
    assert store.outcome_counts() == {"changes-requested": 1}
    assert store.open_requests() == []
