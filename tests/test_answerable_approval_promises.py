"""The three promises FEAT-0159 makes, end to end (TASK-0667).

1. A request without the shell's secret cannot answer a permission prompt
   or put a prompt into a Claude session.
2. An agent other than the principal cannot answer, even with the secret.
3. The secret goes nowhere the agent's terminal, the plugin or the renderer
   can read it.

The fourth promise, that a deny from the person's own PreToolUse hook
survives every cockpit answer, is the plugin's and is tested in
``desktop/plugin/claude-code/tests/approval.test.ts``.
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from project_os_cockpit.approvals import ApprovalStore

from test_agent_hooks import SECRET, _get, _make_workspace, _post, _spin_up

REPO = Path(__file__).resolve().parents[1]


def _wrong_secrets() -> list[str | None]:
    one_off = SECRET[:-1] + ("t" if SECRET[-1] != "t" else "u")
    return [None, "", "t" * 64, one_off, SECRET.upper()]


# ---- 1. no secret, no answer and no delivery ----

@pytest.mark.parametrize("given", _wrong_secrets())
def test_an_answer_without_the_right_secret_changes_nothing(tmp_path: Path, given):
    docs = _make_workspace(tmp_path)
    approval_id = ApprovalStore(docs.parent).ask(
        session_id="s-1", tool="Bash", tool_input={"command": "ls"}, tool_use_id="t-1")["approval_id"]
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, _ = _post(port, "/api/cockpit/approve",
                          {"approval_id": approval_id, "decision": "granted", "actor": "user:edwin"}, given)
        assert status == 403
        assert _get(port, f"/api/cockpit/approvals?approval_id={approval_id}")["approval"]["status"] == "open"
    finally:
        httpd.shutdown()


@pytest.mark.parametrize("given", _wrong_secrets())
def test_a_delivery_without_the_right_secret_is_not_added(tmp_path: Path, given):
    docs = _make_workspace(tmp_path)
    server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, _ = _post(port, "/api/cockpit/deliveries",
                          {"id": "TASK-0001", "prompt": "rm -rf /", "session_id": "s-1"}, given)
        assert status == 403
        assert server.agent_tracker.list_deliveries() == []
    finally:
        httpd.shutdown()


# ---- 2. only a person, or the principal, answers ----

@pytest.mark.parametrize("actor", ["agent:claude", "agent:codex", "Agent:Worker", "AGENT:CLAUDE"])
def test_an_agent_other_than_the_principal_cannot_answer_even_with_the_secret(tmp_path: Path, actor):
    docs = _make_workspace(tmp_path)
    approval_id = ApprovalStore(docs.parent).ask(
        session_id="s-1", tool="Bash", tool_input={"command": "ls"}, tool_use_id="t-1")["approval_id"]
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, body = _post(port, "/api/cockpit/approve",
                             {"approval_id": approval_id, "decision": "granted", "actor": actor}, SECRET)
        assert status == 400 and "may not answer" in body["error"]
        assert _get(port, f"/api/cockpit/approvals?approval_id={approval_id}")["approval"]["status"] == "open"
    finally:
        httpd.shutdown()


def test_the_principal_may_answer_with_the_secret(tmp_path: Path):
    """Edwin, 2026-10-14: a delegated principal keeps the right to answer.
    It can only do so through something that holds the secret."""
    docs = _make_workspace(tmp_path)
    approval_id = ApprovalStore(docs.parent).ask(
        session_id="s-1", tool="Bash", tool_input={"command": "ls"}, tool_use_id="t-1")["approval_id"]
    _server, httpd, port = _spin_up(docs, shell_secret=SECRET)
    try:
        status, body = _post(port, "/api/cockpit/approve",
                             {"approval_id": approval_id, "decision": "granted", "actor": "agent:principal"}, SECRET)
        assert status == 200 and body["result"]["decided_by"] == "agent:principal"
    finally:
        httpd.shutdown()


# ---- 3. the secret goes nowhere it could be read ----

def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_a_sidecar_started_as_the_shell_starts_it_leaks_its_secret_nowhere(tmp_path: Path):
    """Started the way `spawnSidecar` starts it: the secret on one stdin line.
    Then everything the agent's side can read is searched for it."""
    secret = "c0ffee" * 10 + "abcd"
    docs = _make_workspace(tmp_path)
    port = _free_port()
    env = {k: v for k, v in os.environ.items() if not k.startswith("COCKPIT_")}
    env["PYTHONUNBUFFERED"] = "1"
    proc = subprocess.Popen(
        [sys.executable, "-m", "project_os_cockpit", str(docs), "--port", str(port),
         "--bind", "127.0.0.1", "--no-open", "--secret-stdin"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True,
    )
    try:
        proc.stdin.write(json.dumps({"secret": secret, "approval_wait_ms": 5000}) + "\n")
        proc.stdin.close()
        base = f"http://127.0.0.1:{port}"
        for _ in range(100):
            try:
                urllib.request.urlopen(f"{base}/healthz", timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        # Exercise the routes that touch approvals and deliveries.
        ask = json.dumps({"session_id": "s-1", "tool": "Bash", "input": {"command": "ls"},
                          "tool_use_id": "t-1"}).encode()
        urllib.request.urlopen(urllib.request.Request(
            f"{base}/api/cockpit/approvals/ask", data=ask, method="POST",
            headers={"Content-Type": "application/json"}), timeout=3)
        answered = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"{base}/api/cockpit/approve", method="POST",
            data=json.dumps({"approval_id": json.loads(urllib.request.urlopen(
                f"{base}/api/cockpit/approvals", timeout=3).read())["approvals"][0]["approval_id"],
                "decision": "granted", "actor": "user:edwin"}).encode(),
            headers={"Content-Type": "application/json", "X-Cockpit-Secret": secret}), timeout=3).read())
        assert answered["ok"] is True, "the secret on stdin is the one the sidecar requires"

        bodies = [urllib.request.urlopen(f"{base}{p}", timeout=3).read().decode()
                  for p in ("/api/cockpit/state", "/api/cockpit/approvals", "/api/cockpit/deliveries",
                            "/api/cockpit/runtime")]
        assert not any(secret in b for b in bodies), "a response carries the secret"

        # Its command line, as any process of this user can read it.
        argv = subprocess.run(["ps", "-ww", "-o", "command=", "-p", str(proc.pid)],
                              capture_output=True, text=True).stdout
        assert "--secret-stdin" in argv and secret not in argv
        # Its environment, as `ps -E` shows another process's on macOS.
        if sys.platform == "darwin":
            env_view = subprocess.run(["ps", "-E", "-ww", "-o", "command=", "-p", str(proc.pid)],
                                      capture_output=True, text=True).stdout
            assert secret not in env_view
        # Everything it wrote beside the project.
        for f in (docs.parent / ".cockpit").rglob("*"):
            if f.is_file():
                assert secret not in f.read_text(errors="replace"), f
    finally:
        proc.terminate()
        # Not communicate(): before Python 3.13 it flushes stdin, which is
        # closed above, and raises "I/O operation on closed file" (TASK-0677).
        proc.wait(timeout=10)
        err = proc.stderr.read()
        proc.stdout.close()
        proc.stderr.close()
    assert secret not in err, "the sidecar's stderr carries the secret"


def test_only_the_main_process_reads_the_secret():
    """The shell side: `sidecarSecretFor` is the only way to the secret, and
    only the dispatch queue and the approval answer call it. Neither the
    instrument directory, the terminal's environment nor the renderer does."""
    src = REPO / "desktop" / "src"
    callers = sorted(
        str(p.relative_to(src)) for p in src.rglob("*.ts")
        if re.search(r"\bsidecarSecretFor\(", p.read_text(encoding="utf-8"))
        and "export function sidecarSecretFor" not in p.read_text(encoding="utf-8")
    )
    assert callers == ["ipc/approvals.ts", "ipc/dispatch-queue.ts"], callers
    for name in ("agent-instrument.ts", "terminal.ts"):
        text = (src / "ipc" / name).read_text(encoding="utf-8")
        assert "secret" not in text.lower(), f"{name} mentions the secret"
    renderer = (src / "renderer" / "renderer.ts").read_text(encoding="utf-8")
    assert "X-Cockpit-Secret" not in renderer and "sidecarSecretFor" not in renderer
    plugin = (REPO / "desktop" / "plugin" / "claude-code" / "hooks" / "register.ts").read_text(encoding="utf-8")
    assert "X-Cockpit-Secret" not in plugin
