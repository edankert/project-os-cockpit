"""Sidecar identity guard (ISS-0007 / TASK-0146, TST-0017).

A stale ``.cockpit/url`` plus sidecar port reuse can route one repo's
hook events into another repo's sidecar. The guard rejects foreign-cwd
payloads with 409 so the external hook's fallback self-heals into the
correct repo, and ``/api/cockpit/identity`` lets url-file consumers
verify who answered.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _cwd_within_root,
    _make_handler,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_SETTINGS_TS = REPO_ROOT / "desktop" / "src" / "ipc" / "app-settings.ts"


@pytest.fixture()
def live_server(tmp_path):
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
    try:
        yield server, root, f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        httpd.server_close()


def post_hook(base: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{base}/api/agent-hook",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


def test_matching_cwd_ingested(live_server):
    server, root, base = live_server
    status, body = post_hook(base, {
        "hook_event_name": "UserPromptSubmit", "session_id": "own",
        "prompt": "hi", "cwd": str(root),
    })
    assert status == 200 and body["ok"]
    assert server.agent_tracker.sessions_payload()[0]["session_id"] == "own"


def test_subdir_and_case_mangled_cwd_accepted(live_server):
    server, root, base = live_server
    sub = root / "src" / "deep"
    sub.mkdir(parents=True)
    status, _ = post_hook(base, {
        "hook_event_name": "UserPromptSubmit", "session_id": "sub",
        "cwd": str(sub),
    })
    assert status == 200
    # Case-mangled ROOT component (macOS case-insensitivity — the
    # ISS-0001 lesson). Mangling the root is the case that byte-wise
    # prefix matching cannot pass by accident: `/…/PROJ/src/deep`
    # only counts as inside `/…/proj` if the guard folds case. On a
    # case-sensitive filesystem the mangled path doesn't resolve, so
    # only assert where it does.
    mangled = str(sub).replace(f"{os.sep}proj{os.sep}", f"{os.sep}PROJ{os.sep}")
    assert mangled != str(sub)
    status2, _ = post_hook(base, {
        "hook_event_name": "UserPromptSubmit", "session_id": "sub2",
        "cwd": mangled,
    })
    if Path(mangled).exists():
        assert status2 == 200


def test_foreign_cwd_rejected_tracker_clean(live_server, tmp_path):
    server, root, base = live_server
    other = tmp_path / "other-repo"
    other.mkdir()
    status, body = post_hook(base, {
        "hook_event_name": "UserPromptSubmit", "session_id": "foreign",
        "prompt": "poison", "cwd": str(other),
    })
    assert status == 409
    assert body["error"] == "wrong-cockpit"
    sids = [s["session_id"] for s in server.agent_tracker.sessions_payload()]
    assert "foreign" not in sids
    # No agent-state side effects either.
    assert not (root / ".cockpit" / "agent-state.json").exists() or \
        "foreign" not in (root / ".cockpit" / "agent-state.json").read_text()


def test_missing_cwd_accepted(live_server):
    _, _, base = live_server
    status, body = post_hook(base, {
        "hook_event_name": "Statusline", "session_id": "no-cwd",
    })
    assert status == 200 and body["ok"]


def test_identity_endpoint(live_server):
    server, root, base = live_server
    with urllib.request.urlopen(f"{base}/api/cockpit/identity", timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    assert Path(data["root"]).resolve() == root.resolve()
    assert Path(data["docs_root"]).resolve() == (root / "docs").resolve()
    assert isinstance(data["pid"], int)


def test_cwd_within_root_helper(tmp_path):
    root = tmp_path / "repo"
    (root / "sub").mkdir(parents=True)
    assert _cwd_within_root(str(root), root)
    assert _cwd_within_root(str(root / "sub"), root)
    assert not _cwd_within_root(str(tmp_path), root)
    # Sibling with the root as a string prefix must NOT match.
    sibling = tmp_path / "repo-extra"
    sibling.mkdir()
    assert not _cwd_within_root(str(sibling), root)


def test_external_hook_stale_url_self_heals(live_server, tmp_path):
    """ISS-0007 replay: the shipped external hook posts to a WRONG
    repo's sidecar via a stale url; the guard rejects and the hook
    falls back to a file write in the correct repo."""
    server, _, base = live_server  # this sidecar serves `proj`
    src = APP_SETTINGS_TS.read_text(encoding="utf-8")
    m = re.search(
        r"function hookScript\(\): string \{\n  return `(.*?)`;\n\}",
        src, re.DOTALL,
    )
    assert m, "hookScript template not found in app-settings.ts"
    script = tmp_path / "agent-state-hook.py"
    script.write_text(m.group(1), encoding="utf-8")

    victim = tmp_path / "victim-repo"
    (victim / ".cockpit").mkdir(parents=True)
    (victim / "SNAPSHOT.yaml").write_text("version: 1\n", encoding="utf-8")
    # Stale url: victim's file points at proj's sidecar.
    (victim / ".cockpit" / "url").write_text(base, encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({
            "hook_event_name": "UserPromptSubmit",
            "session_id": "victim-session", "prompt": "hello",
            "cwd": str(victim),
        }).encode("utf-8"),
        capture_output=True, timeout=10,
    )
    assert proc.returncode == 0
    # Wrong sidecar stayed clean…
    sids = [s["session_id"] for s in server.agent_tracker.sessions_payload()]
    assert "victim-session" not in sids
    # …and the fallback landed the state in the correct repo.
    state = json.loads(
        (victim / ".cockpit" / "agent-state.json").read_text(encoding="utf-8")
    )
    assert state["state"] == "busy"
    assert state["source"] == "external-hook"
