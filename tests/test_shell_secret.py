"""The shell's secret guards the two routes that make a Claude session act
(FEAT-0159 / TASK-0664).

`POST /api/cockpit/approve` answers a permission prompt, and from FEAT-0159
on that answer runs the command. `POST /api/cockpit/deliveries` turns prompt
text into a Claude turn (RISK-0012). Both now refuse a request that does not
carry the secret the desktop shell made at spawn and wrote to the sidecar's
standard input. Every other route is unchanged, which these tests check too:
the plugin's own posts and `cockpit dispatch` must keep working without it.
"""

from __future__ import annotations

import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from project_os_cockpit import __main__ as entry
from project_os_cockpit.approvals import ApprovalStore

from test_agent_hooks import SECRET, _make_workspace, _post, _spin_up


def _answer(port: int, approval_id: str, secret: str | None) -> tuple[int, dict]:
    return _post(port, "/api/cockpit/approve",
                 {"approval_id": approval_id, "decision": "granted", "actor": "user:edwin"},
                 secret)


def _open_approval(docs: Path) -> str:
    """An open prompt, recorded before the server loads the store."""
    return ApprovalStore(docs.parent).record(session_id="s-1", tool="Bash", prompt="ls")["approval_id"]


def _delivery() -> dict:
    return {"id": "TASK-0001", "prompt": "implement TASK-0001", "session_id": "s-1"}


# ---- the answer route ----

def test_an_answer_without_the_secret_is_refused(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    approval_id = _open_approval(docs)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, body = _answer(port, approval_id, None)
        assert status == 403 and body["ok"] is False
        assert ApprovalStore(docs.parent).open_prompts()[0]["status"] == "open"
    finally:
        httpd.shutdown()


def test_an_answer_with_a_wrong_secret_is_refused_with_the_same_message(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    approval_id = _open_approval(docs)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        missing = _answer(port, approval_id, None)
        wrong = _answer(port, approval_id, "t" * 64)
        assert wrong[0] == 403
        assert wrong[1] == missing[1], "the refusal must not say which: missing or wrong"
    finally:
        httpd.shutdown()


def test_an_answer_with_the_secret_is_recorded(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    approval_id = _open_approval(docs)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, body = _answer(port, approval_id, SECRET)
        assert status == 200 and body["result"]["status"] == "granted"
    finally:
        httpd.shutdown()


@pytest.mark.parametrize("given", [None, "", SECRET])
def test_a_server_started_without_a_secret_refuses_every_answer(tmp_path: Path, given):
    docs = _make_workspace(tmp_path)
    approval_id = _open_approval(docs)
    _server, httpd, port = _spin_up(docs)  # a terminal start: no --secret-stdin
    try:
        status, _ = _answer(port, approval_id, given)
        assert status == 403
    finally:
        httpd.shutdown()


def test_the_content_type_is_refused_before_the_secret_is_looked_at(tmp_path: Path):
    """Loopback, then JSON, then the secret: a framed page's text/plain post
    gets the same 415 it got before this task (ISS-0301)."""
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/api/cockpit/approve", method="POST",
            data=b'{"approval_id":"x","decision":"granted","actor":"user:edwin"}',
            headers={"Content-Type": "text/plain", "X-Cockpit-Secret": SECRET},
        )
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(req, timeout=3)
        assert exc.value.code == 415
    finally:
        httpd.shutdown()


def test_agent_principal_may_still_answer_and_another_agent_may_not(tmp_path: Path):
    """Edwin, 2026-10-14: `approvals.answer` is unchanged by the secret."""
    store = ApprovalStore(tmp_path)
    a = store.record(session_id="s", tool="Bash", prompt="ls")["approval_id"]
    assert store.answer(a, decision="granted", actor="agent:principal")["status"] == "granted"
    b = store.record(session_id="s", tool="Bash", prompt="pwd")["approval_id"]
    with pytest.raises(ValueError):
        store.answer(b, decision="granted", actor="agent:claude")


# ---- the delivery route ----

def test_a_delivery_without_the_secret_is_refused(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, _ = _post(port, "/api/cockpit/deliveries", _delivery())
        assert status == 403
        assert server.agent_tracker.list_deliveries() == []
        status, body = _post(port, "/api/cockpit/deliveries", _delivery(), SECRET)
        assert status == 200 and body["delivery"]["prompt"] == "implement TASK-0001"
    finally:
        httpd.shutdown()


def test_the_plugins_own_delivery_posts_need_no_secret(tmp_path: Path):
    """The plugin must never hold the secret, so its claim, its report of a
    turn's start and its report of a drop stay open to a loopback post."""
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        server.agent_tracker.ingest({"hook_event_name": "SessionStart", "session_id": "s-1",
                                     "agent": "claude", "_cockpit_plugin": True})
        dids = [_post(port, "/api/cockpit/deliveries", _delivery(), SECRET)[1]["delivery"]["did"]
                for _ in range(2)]
        assert _post(port, "/api/cockpit/deliveries/claim", {"did": dids[0]})[0] == 200
        assert _post(port, "/api/cockpit/deliveries/started", {"did": dids[0], "turn_id": "t"})[0] == 200
        assert _post(port, "/api/cockpit/deliveries/claim", {"did": dids[1]})[0] == 200
        assert _post(port, "/api/cockpit/deliveries/dropped", {"did": dids[1], "reason": "x"})[0] == 200
    finally:
        httpd.shutdown()


def test_cockpit_dispatch_from_a_terminal_needs_no_secret(tmp_path: Path):
    """`cockpit dispatch` runs in agent terminals, which must not get the
    secret; it records a request the shell picks up and delivers itself."""
    docs = _make_workspace(tmp_path)
    (docs / "TASK-0001-x.md").write_text(
        '---\ntype: "[[task]]"\nid: TASK-0001\ntitle: x\nstatus: backlog\n---\n# x\n',
        encoding="utf-8")
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, body = _post(port, "/api/cockpit/dispatch", {"id": "TASK-0001", "enqueue": True})
        assert status == 200 and body["ok"] is True
    finally:
        httpd.shutdown()


def test_the_secret_is_in_no_state_response(tmp_path: Path):
    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        for path in ("/api/cockpit/state", "/api/cockpit/approvals", "/api/cockpit/deliveries"):
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=3) as resp:
                assert SECRET not in resp.read().decode("utf-8"), path
    finally:
        httpd.shutdown()


# ---- the line on standard input ----

def test_the_shell_line_gives_the_secret_and_the_wait():
    assert entry.read_shell_line(json.dumps({"secret": SECRET, "approval_wait_ms": 1200})) == (SECRET, 1200)
    assert entry.read_shell_line(json.dumps({"secret": SECRET})) == (SECRET, 5000)


@pytest.mark.parametrize("wait, expect", [(-5, 0), (0, 0), (99999, 30000)])
def test_the_wait_is_clamped(wait, expect):
    assert entry.read_shell_line(json.dumps({"secret": SECRET, "approval_wait_ms": wait}))[1] == expect


@pytest.mark.parametrize("line", [
    "", "not json", "[]", json.dumps({"secret": "short"}), json.dumps({"approval_wait_ms": 5}),
    json.dumps({"secret": SECRET, "approval_wait_ms": True}),
    json.dumps({"secret": SECRET, "approval_wait_ms": "5000"}),
])
def test_a_bad_line_is_refused_without_repeating_it(line):
    with pytest.raises(ValueError) as exc:
        entry.read_shell_line(line)
    assert SECRET not in str(exc.value) and (not line or line not in str(exc.value))


def test_a_bad_line_stops_the_sidecar_before_it_binds(tmp_path: Path, monkeypatch, capsys):
    docs = _make_workspace(tmp_path)
    leaked = json.dumps({"secret": "x" * 10 + "LEAK"})
    monkeypatch.setattr(sys, "stdin", io.StringIO(leaked + "\n"))
    started = []
    monkeypatch.setattr(entry.DocsServer, "run", lambda self: started.append(self))
    assert entry.main([str(docs), "--port", "0", "--secret-stdin"]) == 2
    assert started == []
    assert "LEAK" not in capsys.readouterr().err


def test_without_the_flag_stdin_is_not_read(tmp_path: Path, monkeypatch):
    docs = _make_workspace(tmp_path)

    class Untouchable(io.StringIO):
        def readline(self, *a):  # pragma: no cover - failing is the point
            raise AssertionError("stdin read without --secret-stdin")

    monkeypatch.setattr(sys, "stdin", Untouchable())
    servers = []
    monkeypatch.setattr(entry.DocsServer, "run", lambda self: servers.append(self))
    assert entry.main([str(docs), "--port", "0"]) == 0
    assert servers[0].shell_secret is None


def test_the_flag_hands_the_secret_to_the_server(tmp_path: Path, monkeypatch):
    docs = _make_workspace(tmp_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"secret": SECRET, "approval_wait_ms": 700}) + "\n"))
    servers = []
    monkeypatch.setattr(entry.DocsServer, "run", lambda self: servers.append(self))
    assert entry.main([str(docs), "--port", "0", "--secret-stdin"]) == 0
    assert (servers[0].shell_secret, servers[0].approval_wait_ms) == (SECRET, 700)


def test_a_refusal_closes_a_kept_alive_connection_cleanly(tmp_path: Path):
    """The guard answers before the body is read. Without `Connection: close`
    a keep-alive client sent its next request down that socket and the unread
    body was parsed as a request line: the second answer got 501, not 403
    (found by desktop/tests/shell-secret.test.mjs, 2026-10-14)."""
    import http.client

    docs = _make_workspace(tmp_path)
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        body = json.dumps({"approval_id": "x", "decision": "granted", "actor": "user:edwin"})
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
        for _ in range(2):
            conn.request("POST", "/api/cockpit/approve", body=body,
                         headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            resp.read()
            assert resp.status == 403
            assert resp.getheader("Connection") == "close"
        conn.close()
    finally:
        httpd.shutdown()
