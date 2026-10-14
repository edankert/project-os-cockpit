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
    DELIVERY_REASON_UNCONFIRMED,
    AgentSessionTracker,
)

from test_agent_hooks import SECRET, _get, _make_workspace, _post, _spin_up


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
    # The one being submitted may have started a turn, so it is not held as
    # if it never left (TASK-0662).
    assert states == {"one": ("held", DELIVERY_REASON_ENDED), "two": ("dropped", DELIVERY_REASON_UNCONFIRMED)}
    assert len(tracker.take_delivery_changes()) == 2

    # A held-because-ended delivery is not woken by a later claim, and a new
    # one for the ended session starts held.
    _claim(tracker, "s-a")
    assert {d["state"] for d in tracker.list_deliveries()} == {"held", "dropped"}
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
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    events: list[tuple[str, dict]] = []
    server.bus.subscribe(lambda e: events.append((getattr(e, "event_type", ""), getattr(e, "data", None))))
    try:
        status, body = _post(port, "/api/cockpit/deliveries", {**_item(), "session_id": "s-h"}, SECRET)
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


# ---- cancel (TASK-0657) ----

def test_a_waiting_or_held_delivery_is_cancelled_and_never_claimed(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    waiting, _ = tracker.add_delivery(_item("one"), "s-a")
    cancelled, error = tracker.cancel_delivery(waiting["did"])
    assert error is None and cancelled["state"] == "cancelled" and cancelled["cancelled_at"]
    # The plugin's claim, arriving after the cancel, loses.
    after, error = tracker.move_delivery(waiting["did"], "sending")
    assert error and after["state"] == "cancelled"
    assert tracker.list_deliveries() == []

    held, _ = tracker.add_delivery(_item("two"), "s-unclaimed")
    assert tracker.cancel_delivery(held["did"])[0]["state"] == "cancelled"
    # Cancelling twice is not an error.
    assert tracker.cancel_delivery(held["did"])[1] is None


def test_a_prompt_being_submitted_or_started_cannot_be_cancelled(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    d, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(d["did"], "sending")
    now, error = tracker.cancel_delivery(d["did"])
    assert "being submitted" in error and now["state"] == "sending"
    # The turn then starts, untouched by the refused cancel.
    started, error = tracker.move_delivery(d["did"], "started", turn_id="t-1",
                                           started_at="2026-10-14T14:02:00+00:00")
    assert error is None and started["state"] == "started"
    now, error = tracker.cancel_delivery(d["did"])
    assert "turn has started" in error
    assert (now["state"], now["started_at"], now["turn_id"]) == ("started", "2026-10-14T14:02:00+00:00", "t-1")
    assert [e.get("cancelled") for e in tracker._sessions["s-a"]["dispatches"]] == [None]


def test_a_cancel_and_a_start_end_in_one_state(tmp_path: Path):
    """Whichever arrives first wins, and the loser is told; the delivery never
    ends up both cancelled and delivered."""
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    first, _ = tracker.add_delivery(_item("cancel first"), "s-a")
    tracker.cancel_delivery(first["did"])
    assert tracker.move_delivery(first["did"], "started", turn_id="t")[1]
    second, _ = tracker.add_delivery(_item("claim first"), "s-a")
    tracker.move_delivery(second["did"], "sending")
    assert tracker.cancel_delivery(second["did"])[1]
    tracker.move_delivery(second["did"], "started", turn_id="t-2")
    states = {d["prompt"]: d["state"] for d in tracker._deliveries}
    assert states == {"cancel first": "cancelled", "claim first": "started"}
    history = tracker.dispatch_history("TASK-0001")
    assert [(h.get("cancelled", False), h.get("delivered_by")) for h in history] == [(False, "submit"), (True, None)]


def test_a_cancelled_dispatch_is_in_the_notes_history_and_not_live(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    d, _ = tracker.add_delivery(_item(), "s-a")
    tracker.cancel_delivery(d["did"])
    [entry] = tracker.dispatch_history("TASK-0001")
    assert entry["cancelled"] is True and entry["live"] is False
    assert entry["session_id"] == "s-a" and entry["verb"] == "implement" and entry["ts"]


def test_the_cancel_route(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    events: list[tuple[str, dict]] = []
    server.bus.subscribe(lambda e: events.append((getattr(e, "event_type", ""), getattr(e, "data", None))))
    try:
        _post(port, "/api/agent-hook", {"hook_event_name": "SessionStart", "session_id": "s-c",
                                        "agent": "claude", "_cockpit_plugin": True})
        did = _post(port, "/api/cockpit/deliveries", {**_item(), "session_id": "s-c"}, SECRET)[1]["delivery"]["did"]
        status, body = _post(port, "/api/cockpit/deliveries/cancel", {"did": did})
        assert status == 200 and body["delivery"]["state"] == "cancelled"
        assert _post(port, "/api/cockpit/deliveries/claim", {"did": did})[0] == 409
        assert _post(port, "/api/cockpit/deliveries/cancel", {"did": "nope"})[0] == 404

        did2 = _post(port, "/api/cockpit/deliveries", {**_item(), "session_id": "s-c"}, SECRET)[1]["delivery"]["did"]
        _post(port, "/api/cockpit/deliveries/claim", {"did": did2})
        status, body = _post(port, "/api/cockpit/deliveries/cancel", {"did": did2})
        assert status == 409 and body["delivery"]["state"] == "sending"
        published = [data["state"] for kind, data in events if kind == "cockpit:delivery"]
        assert published == ["waiting", "cancelled", "waiting", "sending"], "a refused cancel publishes nothing"
    finally:
        httpd.shutdown()


def test_a_claude_session_stopped_with_esc_waits_for_the_person(tmp_path: Path):
    """TASK-0659: Claude Code fires no Stop for a turn stopped with Esc, so the
    plugin sends ``Interrupt``. The session then waits for the person, and so
    does every prompt waiting for it, until the person's next prompt."""
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    first, _ = tracker.add_delivery(_item("one"), "s-a")
    tracker.add_delivery(_item("other session"), "s-b")
    tracker.take_delivery_changes()

    def send(event: str, **fields) -> dict:
        return tracker.ingest({"hook_event_name": event, "session_id": "s-a",
                               "agent": "claude", "_cockpit_plugin": True, **fields})

    assert send("UserPromptSubmit", prompt="long work")["state"] == "busy"
    out = send("Interrupt")
    assert (out["state"], out["message"]) == ("needs-input", "interrupted — waiting for your input")
    [marked] = tracker.list_deliveries("s-a")
    assert (marked["did"], marked["state"], marked["waiting_for"]) == (first["did"], "waiting", "you")
    assert [c["did"] for c in tracker.take_delivery_changes()] == [first["did"]], "published once"
    assert "waiting_for" not in tracker.list_deliveries("s-b")[0], "another session's prompt is untouched"

    # A prompt dispatched while it is stopped starts marked; a late tool event
    # does not make the session look busy again.
    late, _ = tracker.add_delivery(_item("two"), "s-a")
    assert late["waiting_for"] == "you"
    assert send("PostToolUse", tool_name="Read")["state"] == "needs-input"

    # The person's next prompt ends the wait, and the marks go with it.
    assert send("UserPromptSubmit", prompt="continue")["state"] == "busy"
    assert all("waiting_for" not in d for d in tracker.list_deliveries("s-a"))
    assert sorted(c["prompt"] for c in tracker.take_delivery_changes()) == ["one", "two"]


def test_a_prompt_unconfirmed_at_session_end_is_never_recorded_as_cancelled(tmp_path: Path):
    """FEAT-0158 review, round 1 (TASK-0662). The plugin claimed a prompt and
    the session ended before it reported the turn's start. The report used to
    be refused and a cancel accepted, so a prompt that ran read as "cancelled,
    before it reached the session"."""
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    d, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(d["did"], "sending")
    tracker.ingest({"hook_event_name": "SessionEnd", "session_id": "s-a",
                    "agent": "claude", "_cockpit_plugin": True})

    # A late report of its turn still counts, and stamps the history.
    started, error = tracker.move_delivery(d["did"], "started", turn_id="t-1",
                                           started_at="2026-10-14T16:00:00+00:00")
    assert error is None and started["state"] == "started" and "reason" not in started
    [entry] = tracker.dispatch_history("TASK-0001")
    assert entry["delivered_by"] == "submit" and entry["turn_id"] == "t-1"


def test_removing_an_unconfirmed_prompt_is_recorded_as_removed(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    d, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(d["did"], "sending")
    tracker.ingest({"hook_event_name": "SessionEnd", "session_id": "s-a",
                    "agent": "claude", "_cockpit_plugin": True})
    gone, error = tracker.cancel_delivery(d["did"])
    assert error is None and gone["state"] == "cancelled"
    [entry] = tracker.dispatch_history("TASK-0001")
    assert entry.get("removed") is True and "cancelled" not in entry
    assert entry["reason"] == DELIVERY_REASON_UNCONFIRMED
    assert entry["live"] is False

    # A dropped prompt that was refused, not unconfirmed, has no late start.
    other, _ = tracker.add_delivery(_item("two", "TASK-0002"), "s-b")
    _claim(tracker, "s-b")
    tracker.move_delivery(other["did"], "sending")
    tracker.move_delivery(other["did"], "dropped", reason="refused")
    assert tracker.move_delivery(other["did"], "started")[1] is not None


def test_a_sidecar_restart_mid_submit_leaves_the_prompt_unconfirmed(tmp_path: Path):
    path = tmp_path / ".cockpit" / "sessions.json"
    tracker = AgentSessionTracker(docs_root=tmp_path, sessions_path=path)
    _claim(tracker, "s-a")
    d, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(d["did"], "sending")

    reborn = AgentSessionTracker(docs_root=tmp_path, sessions_path=path)
    [now] = reborn.list_deliveries("s-a")
    assert (now["state"], now["reason"]) == ("dropped", DELIVERY_REASON_UNCONFIRMED)
    assert reborn.move_delivery(d["did"], "started", turn_id="t-1")[1] is None


def test_prompts_nobody_will_submit_do_not_fill_the_cap(tmp_path: Path):
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    for n in range(DELIVERIES_MAX_OPEN):
        tracker.add_delivery(_item(f"p{n}"), "s-a")
    tracker.ingest({"hook_event_name": "SessionEnd", "session_id": "s-a",
                    "agent": "claude", "_cockpit_plugin": True})
    # Thirty held for an ended session no longer block a new dispatch.
    assert tracker.add_delivery(_item("new"), "s-b")[1] is None


def test_a_removed_prompt_is_not_live_work_in_a_live_session(tmp_path: Path):
    """The re-dispatch guard reads `live`. A prompt Claude refused, removed
    from the queue list while its session still runs, is not live work there
    (TASK-0662; round 2 found the term untested)."""
    tracker = AgentSessionTracker(docs_root=tmp_path)
    _claim(tracker, "s-a")
    d, _ = tracker.add_delivery(_item(), "s-a")
    tracker.move_delivery(d["did"], "sending")
    tracker.move_delivery(d["did"], "dropped", reason="refused")
    tracker.cancel_delivery(d["did"])
    [entry] = tracker.dispatch_history("TASK-0001")
    assert entry.get("removed") is True
    assert entry["live"] is False
