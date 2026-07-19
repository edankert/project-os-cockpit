"""External agent-state hook (FEAT-0027 / TASK-0141, TST-0015).

The hook script ships embedded in ``desktop/src/ipc/app-settings.ts``
(the desktop app writes it under its userData when the settings toggle
is enabled). These tests extract that exact script and run it the way
Claude Code would — payload on stdin — so the shipped bytes are what's
verified.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _make_handler,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_SETTINGS_TS = REPO_ROOT / "desktop" / "src" / "ipc" / "app-settings.ts"


@pytest.fixture(scope="module")
def hook_script(tmp_path_factory) -> Path:
    src = APP_SETTINGS_TS.read_text(encoding="utf-8")
    m = re.search(
        r"function hookScript\(\): string \{\n  return `(.*?)`;\n\}",
        src, re.DOTALL,
    )
    assert m, "hookScript template not found in app-settings.ts"
    script = tmp_path_factory.mktemp("hook") / "agent-state-hook.py"
    script.write_text(m.group(1), encoding="utf-8")
    return script


def run_hook(script: Path, payload: dict) -> int:
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload).encode("utf-8"),
        capture_output=True, timeout=10,
    )
    return proc.returncode


def test_noop_outside_project_os(hook_script: Path, tmp_path: Path):
    plain = tmp_path / "plain-repo"
    plain.mkdir()
    rc = run_hook(hook_script, {
        "hook_event_name": "UserPromptSubmit", "cwd": str(plain),
    })
    assert rc == 0
    assert not (plain / ".cockpit").exists()


def test_file_fallback_state_mapping(hook_script: Path, tmp_path: Path):
    root = tmp_path / "proj"
    (root / "sub" / "dir").mkdir(parents=True)
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    state_file = root / ".cockpit" / "agent-state.json"
    # cwd deep inside the repo — the walk-up finds SNAPSHOT.yaml.
    for event, expected in (
        ("UserPromptSubmit", "busy"),
        ("PermissionRequest", "needs-input"),
        ("Stop", "waiting"),
        ("SessionEnd", "idle"),
    ):
        rc = run_hook(hook_script, {
            "hook_event_name": event, "cwd": str(root / "sub" / "dir"),
        })
        assert rc == 0
        data = json.loads(state_file.read_text(encoding="utf-8"))
        assert data["state"] == expected
        assert data["source"] == "external-hook"
    # Unknown events change nothing and exit clean.
    before = state_file.read_text(encoding="utf-8")
    assert run_hook(hook_script, {
        "hook_event_name": "SomethingNew", "cwd": str(root),
    }) == 0
    assert state_file.read_text(encoding="utf-8") == before


def test_file_fallback_notification_severity(hook_script: Path, tmp_path: Path):
    """The file-fallback path gates Notification by subtype, matching
    the sidecar tracker (TASK-0156/0153): blocking subtypes → needs-input,
    idle_prompt → waiting, others → no write."""
    root = tmp_path / "proj"
    root.mkdir()
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    state_file = root / ".cockpit" / "agent-state.json"
    for ntype, expected in (
        ("permission_prompt", "needs-input"),
        ("elicitation_dialog", "needs-input"),
        ("idle_prompt", "waiting"),
    ):
        assert run_hook(hook_script, {
            "hook_event_name": "Notification",
            "notification_type": ntype, "cwd": str(root),
        }) == 0
        assert json.loads(state_file.read_text())["state"] == expected
    # A non-attention notification subtype writes nothing.
    before = state_file.read_text(encoding="utf-8")
    assert run_hook(hook_script, {
        "hook_event_name": "Notification",
        "notification_type": "progress", "cwd": str(root),
    }) == 0
    assert state_file.read_text(encoding="utf-8") == before


def test_stale_url_falls_back_to_file(hook_script: Path, tmp_path: Path):
    root = tmp_path / "proj"
    (root / ".cockpit").mkdir(parents=True)
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    (root / ".cockpit" / "url").write_text("http://127.0.0.1:1", encoding="utf-8")
    rc = run_hook(hook_script, {
        "hook_event_name": "Stop", "cwd": str(root),
    })
    assert rc == 0
    data = json.loads((root / ".cockpit" / "agent-state.json").read_text())
    assert data["state"] == "waiting"


def test_posts_to_live_sidecar(hook_script: Path, tmp_path: Path):
    root = tmp_path / "proj"
    docs = root / "docs"
    docs.mkdir(parents=True)
    (docs / "README.md").write_text("# Hi\n", encoding="utf-8")
    (root / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
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
    (root / ".cockpit").mkdir(exist_ok=True)
    (root / ".cockpit" / "url").write_text(
        f"http://127.0.0.1:{port}", encoding="utf-8",
    )
    try:
        rc = run_hook(hook_script, {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "ext-test", "prompt": "external hello",
            "cwd": str(root),
        })
        assert rc == 0
        # Full pipeline: the tracker saw the session, not just a dot.
        sessions = server.agent_tracker.sessions_payload()
        assert sessions[0]["session_id"] == "ext-test"
        assert sessions[0]["last_prompt"] == "external hello"
    finally:
        httpd.shutdown()
        httpd.server_close()
