"""A Claude permission ask offered to the cockpit (FEAT-0159 / TASK-0665).

The cockpit plugin's `tool.check` hook posts the ask, polls its record for
the workspace's wait, and hands it back to the terminal when the wait runs
out. These run the sidecar's half on a loopback server: the routes, the
store's states, and the hook events that close a record.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

from project_os_cockpit.approvals import HANDED_BACK, MAX_INPUT_BYTES, ApprovalStore

from test_agent_hooks import SECRET, _get, _hook, _make_workspace, _post, _spin_up


def _ask(port: int, tool_use_id: str = "toolu_1", **over) -> tuple[int, dict]:
    body = {"session_id": "s-1", "tool": "Bash", "input": {"command": "rm -rf build"},
            "tool_use_id": tool_use_id, **over}
    return _post(port, "/api/cockpit/approvals/ask", body)


def _answer(port: int, approval_id: str, decision: str = "granted") -> tuple[int, dict]:
    return _post(port, "/api/cockpit/approve",
                 {"approval_id": approval_id, "decision": decision, "actor": "user:edwin"}, SECRET)


def _record(port: int, approval_id: str) -> dict:
    return _get(port, f"/api/cockpit/approvals?approval_id={approval_id}")["approval"]


def test_an_ask_is_recorded_once_per_tool_call_with_its_command_in_full(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    events: list[str] = []
    server.bus.subscribe(lambda e: events.append(getattr(e, "event_type", "")))
    try:
        status, first = _ask(port)
        assert status == 200 and first["wait_ms"] == 5000
        _, again = _ask(port)
        assert again["approval_id"] == first["approval_id"], "one tool call is one approval"
        record = _record(port, first["approval_id"])
        assert (record["status"], record["prompt"], record["tool_use_id"]) == ("open", "rm -rf build", "toolu_1")
        assert "cockpit:approval" in events
        live = _get(port, "/api/cockpit/approvals")["approvals"]
        assert [a["approval_id"] for a in live] == [first["approval_id"]]
    finally:
        httpd.shutdown()


def test_another_sessions_offer_with_the_same_call_id_gets_its_own_record(tmp_path: Path):
    """FEAT-0159 review, round 1: the record is one per session and call, so
    an offer from elsewhere cannot put its input on this session's card."""
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        _, first = _ask(port, session_id="s-other", input={"command": "echo harmless"})
        _, mine = _ask(port)
        assert mine["approval_id"] != first["approval_id"]
        record = _record(port, mine["approval_id"])
        assert (record["session_id"], record["prompt"]) == ("s-1", "rm -rf build")
    finally:
        httpd.shutdown()


def test_another_sessions_finished_call_with_the_same_id_leaves_the_card_open(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        mine = _ask(port, "toolu_a")[1]["approval_id"]
        _hook(port, {"hook_event_name": "PostToolUse", "session_id": "s-other",
                     "tool_name": "Bash", "tool_use_id": "toolu_a", "agent": "claude"})
        assert _record(port, mine)["status"] == "open"
    finally:
        httpd.shutdown()


def test_a_long_command_is_not_offered(tmp_path: Path):
    """A person must read what they approve in full; a longer one stays in the
    terminal rather than being shown cut short."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, body = _ask(port, input={"command": "x" * (MAX_INPUT_BYTES + 1)})
        assert status == 200 and (body["approval_id"], body["wait_ms"]) == (None, 0)
        assert _get(port, "/api/cockpit/approvals")["approvals"] == []
        # Just under the limit is offered, and kept whole.
        command = "y" * (MAX_INPUT_BYTES - 100)
        _, ok = _ask(port, tool_use_id="toolu_2", input={"command": command})
        assert _record(port, ok["approval_id"])["prompt"] == command
    finally:
        httpd.shutdown()


def test_a_workspace_with_no_wait_offers_nothing(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET, approval_wait_ms=0)
    try:
        assert _ask(port)[1]["wait_ms"] == 0
        assert _get(port, "/api/cockpit/approvals")["approvals"] == []
    finally:
        httpd.shutdown()


def test_handed_back_after_a_click_returns_the_click(tmp_path: Path):
    """The click and the end of the wait can cross. Whichever reaches the
    store first decides, and the plugin uses what handed-back returns."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        approval_id = _ask(port)[1]["approval_id"]
        assert _answer(port, approval_id)[0] == 200
        status, body = _post(port, "/api/cockpit/approvals/handed-back", {"approval_id": approval_id})
        assert status == 200 and body["approval"]["status"] == "granted"
    finally:
        httpd.shutdown()


def test_an_answer_after_the_wait_ran_out_is_refused(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        approval_id = _ask(port)[1]["approval_id"]
        _, body = _post(port, "/api/cockpit/approvals/handed-back", {"approval_id": approval_id})
        assert body["approval"]["status"] == "handed-to-terminal"
        status, late = _answer(port, approval_id)
        assert status == 409 and late["error"] == HANDED_BACK
        assert _record(port, approval_id)["status"] == "handed-to-terminal"
        # Still listed, so the card can say the terminal has it.
        assert [a["status"] for a in _get(port, "/api/cockpit/approvals")["approvals"]] == ["handed-to-terminal"]
    finally:
        httpd.shutdown()


def test_a_second_answer_is_refused_and_the_first_stands(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        approval_id = _ask(port)[1]["approval_id"]
        assert _answer(port, approval_id, "denied")[0] == 200
        status, body = _answer(port, approval_id, "granted")
        assert status == 409 and body["approval"]["status"] == "denied"
    finally:
        httpd.shutdown()


def test_the_call_running_closes_its_approval(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        a = _ask(port, "toolu_a")[1]["approval_id"]
        b = _ask(port, "toolu_b")[1]["approval_id"]
        _hook(port, {"hook_event_name": "PostToolUse", "session_id": "s-1",
                     "tool_name": "Bash", "tool_use_id": "toolu_a", "agent": "claude"})
        assert _record(port, a)["status"] == "closed"
        assert _record(port, b)["status"] == "open", "only the call that ran"
        assert _answer(port, a)[0] == 409
    finally:
        httpd.shutdown()


def test_the_session_ending_closes_its_approvals(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        mine = _ask(port, "toolu_a")[1]["approval_id"]
        other = _ask(port, "toolu_b", session_id="s-2")[1]["approval_id"]
        _hook(port, {"hook_event_name": "SessionEnd", "session_id": "s-1", "agent": "claude"})
        assert _record(port, mine)["status"] == "closed"
        assert _record(port, other)["status"] == "open"
    finally:
        httpd.shutdown()


def test_an_ask_needs_a_real_call(tmp_path: Path):
    """A `$.tool.check` query has no tool_use_id and is never offered."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        assert _ask(port, tool_use_id="")[0] == 400
    finally:
        httpd.shutdown()


def test_an_unknown_approval_is_404(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/cockpit/approvals?approval_id=nope", timeout=3)
            raise AssertionError("expected 404")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        assert _post(port, "/api/cockpit/approvals/handed-back", {"approval_id": "nope"})[0] == 404
    finally:
        httpd.shutdown()


def test_escalation_still_counts_only_open_prompts(tmp_path: Path):
    store = ApprovalStore(tmp_path)
    a = store.ask(session_id="s", tool="Bash", tool_input={"command": "ls"}, tool_use_id="t1")
    store.ask(session_id="s", tool="Bash", tool_input={"command": "pwd"}, tool_use_id="t2")
    store.hand_back(a["approval_id"])
    assert [p["tool_use_id"] for p in store.open_prompts()] == ["t2"]
    assert len(store.live_prompts()) == 2


def test_the_end_of_a_main_loop_turn_closes_a_prompt_refused_in_the_terminal(tmp_path: Path):
    """A call refused in the terminal never runs, so no PostToolUse closes
    its record; the turn ending does (live run, 2026-10-14). A subagent's ask
    is left open, because a background subagent can outlive the turn."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        refused = _ask(port, "toolu_a")[1]["approval_id"]
        _post(port, "/api/cockpit/approvals/handed-back", {"approval_id": refused})
        sub = _ask(port, "toolu_b", agent_id="agent-1")[1]["approval_id"]
        other = _ask(port, "toolu_c", session_id="s-2")[1]["approval_id"]
        _hook(port, {"hook_event_name": "Stop", "session_id": "s-1", "agent": "claude"})
        assert _record(port, refused)["status"] == "closed"
        assert _record(port, sub)["status"] == "open"
        assert _record(port, other)["status"] == "open"
        _hook(port, {"hook_event_name": "Interrupt", "session_id": "s-2", "agent": "claude"})
        assert _record(port, other)["status"] == "closed"
        # Esc on the terminal's dialog sends neither; the next prompt closes it.
        third = _ask(port, "toolu_d")[1]["approval_id"]
        _post(port, "/api/cockpit/approvals/handed-back", {"approval_id": third})
        _hook(port, {"hook_event_name": "UserPromptSubmit", "session_id": "s-1", "agent": "claude",
                     "prompt": "do something else"})
        assert _record(port, third)["status"] == "closed"
        assert _record(port, sub)["status"] == "open"
    finally:
        httpd.shutdown()
