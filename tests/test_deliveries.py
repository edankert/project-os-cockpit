"""Deliveries: a dispatched prompt addressed to one Claude session, which the
cockpit plugin submits once the session is idle (FEAT-0158 / TASK-0654).

The tracker tests drive ``AgentSessionTracker`` directly; the HTTP test runs
the real routes on a loopback server and watches the event bus.
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit.agent_hooks import (
    DELIVERIES_MAX_OPEN,
    DELIVERY_REASON_ENDED,
    DELIVERY_REASON_UNCLAIMED,
    AgentSessionTracker,
)

from test_agent_hooks import _get, _make_workspace, _post, _spin_up


def _claim(tracker: AgentSessionTracker, sid: str) -> None:
    """The plugin's first post claims the session."""
    tracker.ingest({"hook_event_name": "SessionStart", "session_id": sid,
                    "agent": "claude", "_cockpit_plugin": True})


def _item(prompt: str = "implement TASK-0001", note: str = "TASK-0001") -> dict:
    return {"id": note, "prompt": prompt, "verb": "implement", "rel": "tasks/x.md"}


def test_a_delivery_is_held_until_the_plugin_claims_its_session(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    delivery, error = tracker.add_delivery(_item(), "s-a")
    assert error is None
    assert (delivery["state"], delivery["reason"]) == ("held", DELIVERY_REASON_UNCLAIMED)

    # An unmarked post (the external hook) does not claim the session.
    tracker.ingest({"hook_event_name": "UserPromptSubmit", "session_id": "s-a",
                    "agent": "claude", "prompt": "hi"})
    assert tracker.list_deliveries("s-a")[0]["state"] == "held"

    _claim(tracker, "s-a")
    [now] = tracker.list_deliveries("s-a")
    assert now["state"] == "waiting" and "reason" not in now
    changes = tracker.take_delivery_changes()
    assert [c["state"] for c in changes] == ["waiting"], "the change is handed to the server to publish"
    assert tracker.take_delivery_changes() == []


def test_a_delivery_to_a_claimed_session_starts_waiting(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    delivery, _ = tracker.add_delivery(_item(), "s-a")
    assert delivery["state"] == "waiting"
    assert delivery["id"] == "TASK-0001" and delivery["prompt"] == "implement TASK-0001"


def test_one_sessions_deliveries_are_not_listed_for_another(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    _claim(tracker, "s-b")
    tracker.add_delivery(_item("for a"), "s-a")
    tracker.add_delivery(_item("for b"), "s-b")
    assert [d["prompt"] for d in tracker.list_deliveries("s-a")] == ["for a"]
    assert [d["prompt"] for d in tracker.list_deliveries("s-b")] == ["for b"]
    assert [d["prompt"] for d in tracker.list_deliveries()] == ["for a", "for b"]


def test_a_claim_is_refused_unless_the_delivery_is_waiting(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    held, _ = tracker.add_delivery(_item(), "s-a")
    now, error = tracker.move_delivery(held["did"], "sending")
    assert error and now["state"] == "held", "a held delivery cannot be claimed"

    _claim(tracker, "s-a")
    claimed, error = tracker.move_delivery(held["did"], "sending")
    assert error is None and claimed["state"] == "sending"
    again, error = tracker.move_delivery(held["did"], "sending")
    assert error and again["state"] == "sending", "the second of two claims loses"

    # A cancelled delivery (TASK-0657 adds the route) is never claimed.
    other, _ = tracker.add_delivery(_item("second"), "s-a")
    tracker._deliveries[-1]["state"] = "cancelled"
    after, error = tracker.move_delivery(other["did"], "sending")
    assert error and after["state"] == "cancelled"

    missing, error = tracker.move_delivery("nope", "sending")
    assert missing is None and error == "no such delivery"


def test_started_stamps_the_ledger_on_its_own_session_at_the_turns_start(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    delivery, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(delivery["did"], "sending")
    # Another session is the newest live one: a ledger write that picks "the
    # live session", as record_dispatch does, would land there.
    _claim(tracker, "s-b")
    tracker.ingest({"hook_event_name": "UserPromptSubmit", "session_id": "s-b",
                    "agent": "claude", "prompt": "other work", "_cockpit_plugin": True})

    turn_start = "2026-10-14T14:02:00.000+00:00"
    started, error = tracker.move_delivery(delivery["did"], "started",
                                           turn_id="turn-7", started_at=turn_start)
    assert error is None and started["state"] == "started"
    assert tracker._sessions["s-b"].get("dispatches") == []
    [entry] = tracker._sessions["s-a"]["dispatches"]
    assert entry == {"id": "TASK-0001", "ts": turn_start, "agent": "claude",
                     "verb": "implement", "delivered_by": "submit",
                     "turn_id": "turn-7", "delivery": delivery["did"]}
    history = tracker.dispatch_history("TASK-0001")
    assert [(h["session_id"], h["ts"]) for h in history] == [("s-a", turn_start)]
    assert tracker.list_deliveries() == [], "a started delivery leaves the list"

    # A turn can only start once.
    _, error = tracker.move_delivery(delivery["did"], "started", turn_id="turn-8")
    assert error and len(tracker._sessions["s-a"]["dispatches"]) == 1


def test_started_is_refused_before_the_plugin_claimed_it(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    delivery, _ = tracker.add_delivery(_item(), "s-a")
    _, error = tracker.move_delivery(delivery["did"], "started", turn_id="t")
    assert error and tracker._sessions["s-a"]["dispatches"] == []


def test_a_dropped_prompt_keeps_its_reason_and_stays_listed(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    delivery, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(delivery["did"], "sending")
    dropped, error = tracker.move_delivery(delivery["did"], "dropped", reason="blocked by a hook")
    assert error is None
    assert (dropped["state"], dropped["reason"]) == ("dropped", "blocked by a hook")
    assert [d["state"] for d in tracker.list_deliveries()] == ["dropped"]


def test_a_session_that_ends_holds_what_was_on_its_way(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    waiting, _ = tracker.add_delivery(_item("one"), "s-a")
    sending, _ = tracker.add_delivery(_item("two"), "s-a")
    tracker.move_delivery(sending["did"], "sending")
    tracker.take_delivery_changes()
    tracker.ingest({"hook_event_name": "SessionEnd", "session_id": "s-a",
                    "agent": "claude", "_cockpit_plugin": True})
    states = {d["prompt"]: (d["state"], d.get("reason")) for d in tracker.list_deliveries()}
    assert states == {"one": ("held", DELIVERY_REASON_ENDED), "two": ("held", DELIVERY_REASON_ENDED)}
    assert len(tracker.take_delivery_changes()) == 2

    # A held-because-ended delivery is not woken by a later claim, and a new
    # one for the ended session starts held.
    _claim(tracker, "s-a")
    assert {d["state"] for d in tracker.list_deliveries()} == {"held"}
    late, _ = tracker.add_delivery(_item("three"), "s-a")
    assert (late["state"], late["reason"]) == ("held", DELIVERY_REASON_ENDED)


def test_deliveries_survive_a_sidecar_restart_as_held(tmp_path: Path):
    path = tmp_path / ".cockpit" / "sessions.json"
    tracker = AgentSessionTracker(docs_root=tmp_path, sessions_path=path)
    _claim(tracker, "s-a")
    tracker.add_delivery(_item(), "s-a")

    reborn = AgentSessionTracker(docs_root=tmp_path, sessions_path=path)
    [held] = reborn.list_deliveries("s-a")
    assert (held["state"], held["reason"]) == ("held", DELIVERY_REASON_ENDED)


def test_at_most_thirty_prompts_wait_in_a_workspace(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    for n in range(DELIVERIES_MAX_OPEN):
        assert tracker.add_delivery(_item(f"p{n}"), "s-a")[1] is None
    delivery, error = tracker.add_delivery(_item("one too many"), "s-a")
    assert delivery is None and str(DELIVERIES_MAX_OPEN) in error


def test_a_delivery_needs_a_prompt_a_note_and_a_session(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    assert tracker.add_delivery({"id": "TASK-1", "prompt": " "}, "s-a")[1] == "missing 'prompt'"
    assert tracker.add_delivery({"prompt": "x"}, "s-a")[1] == "missing 'id'"
    assert tracker.add_delivery({"id": "TASK-1", "prompt": "x"}, "")[1] == "missing 'session_id'"


def test_the_routes_move_a_delivery_and_publish_each_change(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs)
    events: list[tuple[str, dict]] = []
    server.bus.subscribe(lambda e: events.append((getattr(e, "event_type", ""), getattr(e, "data", None))))
    try:
        status, body = _post(port, "/api/cockpit/deliveries", {**_item(), "session_id": "s-h"})
        assert status == 200 and body["delivery"]["state"] == "held"
        did = body["delivery"]["did"]

        # The plugin's first post claims the session; the change is published.
        _post(port, "/api/agent-hook", {"hook_event_name": "SessionStart", "session_id": "s-h",
                                        "agent": "claude", "_cockpit_plugin": True})
        listed = _get(port, "/api/cockpit/deliveries?session=s-h")["deliveries"]
        assert [d["state"] for d in listed] == ["waiting"]
        assert _get(port, "/api/cockpit/deliveries?session=other")["deliveries"] == []

        assert _post(port, "/api/cockpit/deliveries/claim", {"did": did})[0] == 200
        status, body = _post(port, "/api/cockpit/deliveries/claim", {"did": did})
        assert status == 409 and body["delivery"]["state"] == "sending"
        assert _post(port, "/api/cockpit/deliveries/claim", {"did": "nope"})[0] == 404

        status, body = _post(port, "/api/cockpit/deliveries/started",
                             {"did": did, "turn_id": "turn-1", "started_at": "2026-10-14T14:00:00.000+00:00"})
        assert status == 200 and body["delivery"]["state"] == "started"

        assert _get(port, "/api/cockpit/state")["session"]["plugin_claimed"] is True

        published = [data["state"] for kind, data in events if kind == "cockpit:delivery"]
        assert published == ["held", "waiting", "sending", "started"]
    finally:
        httpd.shutdown()


def test_a_session_payload_says_whether_the_plugin_speaks_for_it(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    assert tracker.snapshot()["session"]["plugin_claimed"] is True
    tracker.ingest({"hook_event_name": "SessionEnd", "session_id": "s-a",
                    "agent": "claude", "_cockpit_plugin": True})
    tracker.ingest({"hook_event_name": "SessionStart", "session_id": "s-b", "agent": "claude"})
    assert tracker.snapshot()["session"]["session_id"] == "s-b"
    assert tracker.snapshot()["session"]["plugin_claimed"] is False


def test_a_typed_dispatch_is_marked_typed_in_the_ledger(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    tracker.ingest({"hook_event_name": "SessionStart", "session_id": "s-c", "agent": "codex"})
    rec = tracker.record_dispatch("TASK-0002", verb="implement", agent="codex", delivered_by="typed")
    assert rec["delivered_by"] == "typed"
    assert tracker._sessions["s-c"]["dispatches"][-1]["delivered_by"] == "typed"
    assert "delivered_by" not in tracker.record_dispatch("TASK-0003", delivered_by="other")


def test_the_state_payload_counts_open_deliveries(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    first, _ = tracker.add_delivery(_item("one"), "s-a")
    tracker.add_delivery(_item("two"), "s-a")
    assert tracker.snapshot()["deliveries_open"] == 2
    tracker.move_delivery(first["did"], "sending")
    tracker.move_delivery(first["did"], "started", turn_id="t")
    assert tracker.snapshot()["deliveries_open"] == 1
