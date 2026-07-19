"""Sidecar contract tests for FEAT-0007 / TASK-0059.

Exercises the three additive surface points the Electron desktop shell
depends on:

* ``COCKPIT_DESKTOP=1`` environment-variable gate (``_desktop_mode``).
* ``GET /healthz`` — liveness + identity probe.
* Terminal endpoint short-circuits to ``enabled: false`` in desktop mode
  (the shell mounts a native ``node-pty`` pane instead).

The Flask-style per-project mode (mode 1) must be unaffected — every
test below either explicitly sets / unsets the env var, leaving the
default code path untouched.
"""

from __future__ import annotations

import json
import socket
import threading
import urllib.request
from pathlib import Path

from project_os_cockpit import server as server_module
from project_os_cockpit.server import (
    DocsServer,
    _NoDNSThreadingHTTPServer,
    _desktop_mode,
    _make_handler,
)
from project_os_cockpit.terminal import TerminalProcess


# ---- _desktop_mode helper ----

def test_desktop_mode_false_by_default(monkeypatch) -> None:
    monkeypatch.delenv("COCKPIT_DESKTOP", raising=False)
    assert _desktop_mode() is False


def test_desktop_mode_true_when_env_set(monkeypatch) -> None:
    monkeypatch.setenv("COCKPIT_DESKTOP", "1")
    assert _desktop_mode() is True


def test_desktop_mode_false_when_env_not_one(monkeypatch) -> None:
    """Only the exact value ``"1"`` activates desktop mode; ``true`` /
    ``yes`` / empty string do not. Avoids accidental activation if a
    user has the variable set for some unrelated reason."""
    monkeypatch.setenv("COCKPIT_DESKTOP", "true")
    assert _desktop_mode() is False
    monkeypatch.setenv("COCKPIT_DESKTOP", "")
    assert _desktop_mode() is False


# ---- /healthz endpoint ----

def _spin_up_server(tmp_path: Path) -> tuple[DocsServer, _NoDNSThreadingHTTPServer, int, threading.Thread]:
    """Spin up the request handler against a temp docs dir on an
    ephemeral port. Mirrors the pattern in ``test_cockpit_state.py``."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# hi\n", encoding="utf-8")
    server = DocsServer(docs_root=docs, bind="127.0.0.1", port=0)
    httpd = _NoDNSThreadingHTTPServer(
        ("127.0.0.1", 0),
        _make_handler(
            server.docs_root, server.index, server.bus,
            cockpit_state=server.cockpit_state,
        ),
    )
    port = httpd.server_address[1]
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return server, httpd, port, th


def test_healthz_returns_service_identity(tmp_path: Path, monkeypatch) -> None:
    """``GET /healthz`` returns the identity payload the Electron shell
    polls for during sidecar startup. Mode 1 (env unset) shows
    ``desktop_mode: false`` so the shell can refuse to attach to a
    sidecar that isn't actually configured for desktop use."""
    monkeypatch.delenv("COCKPIT_DESKTOP", raising=False)
    _server, httpd, port, _th = _spin_up_server(tmp_path)
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/healthz", timeout=2
        ) as resp:
            assert resp.status == 200
            assert resp.headers["Content-Type"].startswith("application/json")
            body = json.loads(resp.read().decode("utf-8"))
        assert body["ok"] is True
        assert body["service"] == "project-os-cockpit"
        assert isinstance(body["schema"], int)
        assert body["docs_root"].endswith("docs")
        assert body["desktop_mode"] is False
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_healthz_reports_desktop_mode(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("COCKPIT_DESKTOP", "1")
    _server, httpd, port, _th = _spin_up_server(tmp_path)
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/healthz", timeout=2
        ) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        assert body["desktop_mode"] is True
    finally:
        httpd.shutdown()
        httpd.server_close()


# ---- Terminal short-circuit in desktop mode ----

def test_terminal_is_available_false_in_desktop_mode(monkeypatch) -> None:
    """Even if ttyd is installed, desktop mode hides it — the Electron
    shell mounts its own native pane in the same slot."""
    monkeypatch.setenv("COCKPIT_DESKTOP", "1")
    # Pretend ttyd IS on PATH; the env-var must still suppress it.
    monkeypatch.setattr(
        "project_os_cockpit.terminal.shutil.which",
        lambda name: "/usr/local/bin/ttyd",
    )
    assert TerminalProcess.is_available() is False


def test_terminal_info_in_desktop_mode_returns_specific_reason(
    tmp_path: Path, monkeypatch,
) -> None:
    """The JS client branches on ``enabled``; the ``reason`` string
    should clearly identify desktop mode rather than the generic
    'ttyd missing' install hint, so debugging is unambiguous."""
    monkeypatch.setenv("COCKPIT_DESKTOP", "1")
    info = TerminalProcess(working_dir=tmp_path).info()
    assert info["enabled"] is False
    assert "desktop" in str(info["reason"]).lower()
    # In desktop mode the install hint is wrong — make sure we suppress it.
    assert "brew install" not in str(info["reason"]).lower()


def test_terminal_info_unchanged_outside_desktop_mode(
    tmp_path: Path, monkeypatch,
) -> None:
    """Mode 1 regression guard: with no env var and no ttyd on PATH,
    the existing install hint must still appear."""
    monkeypatch.delenv("COCKPIT_DESKTOP", raising=False)
    monkeypatch.setattr(
        "project_os_cockpit.terminal.shutil.which", lambda name: None
    )
    info = TerminalProcess(working_dir=tmp_path).info()
    assert info["enabled"] is False
    assert "ttyd" in str(info["reason"]).lower()
    assert "desktop" not in str(info["reason"]).lower()


# ---- Discovery file ----
#
# Since FEAT-0027 the discovery file is written in BOTH modes —
# external terminals need it to reach desktop sidecars (`cockpit
# focus/dispatch`, external agent-state hook). ``run()`` blocks on
# ``serve_forever()``, so we exercise the writer directly.

def test_discovery_file_written_in_both_modes(
    tmp_path: Path, monkeypatch,
) -> None:
    for env in (None, "1"):
        if env is None:
            monkeypatch.delenv("COCKPIT_DESKTOP", raising=False)
        else:
            monkeypatch.setenv("COCKPIT_DESKTOP", env)
        project_root = tmp_path / f"proj-{env or 'browser'}"
        project_root.mkdir()
        server_module._write_discovery_file(project_root, "http://127.0.0.1:8765")
        assert (project_root / ".cockpit" / "url").read_text().strip() == (
            "http://127.0.0.1:8765"
        )
