"""Unit tests for :mod:`project_os_cockpit.terminal`.

ttyd is an external binary; tests cover the parts that don't need
ttyd actually running (binary detection, port allocation, info()
fallback when ttyd is absent).
"""

from __future__ import annotations

from pathlib import Path

from project_os_cockpit.terminal import TerminalProcess


def test_is_available_returns_bool() -> None:
    assert isinstance(TerminalProcess.is_available(), bool)


def test_free_port_is_local_loopback() -> None:
    port = TerminalProcess._free_port()
    assert isinstance(port, int)
    assert 1024 < port < 65536


def test_info_returns_install_hint_when_ttyd_missing(
    tmp_path: Path, monkeypatch
) -> None:
    """When ``shutil.which('ttyd')`` returns None, info() must surface a
    helpful reason string and never raise."""
    monkeypatch.setattr(
        "project_os_cockpit.terminal.shutil.which", lambda name: None
    )
    proc = TerminalProcess(working_dir=tmp_path)
    info = proc.info()
    assert info["enabled"] is False
    assert "ttyd" in str(info.get("reason", "")).lower()


def test_default_command_is_user_shell(tmp_path: Path, monkeypatch) -> None:
    """Default command falls back to ``$SHELL`` (or ``/bin/bash``)."""
    monkeypatch.setenv("SHELL", "/usr/bin/fish")
    proc = TerminalProcess(working_dir=tmp_path)
    assert proc.command == ["/usr/bin/fish"]


def test_command_override(tmp_path: Path) -> None:
    proc = TerminalProcess(working_dir=tmp_path, command=["claude-code"])
    assert proc.command == ["claude-code"]


def test_stop_is_idempotent(tmp_path: Path) -> None:
    """Calling stop() on a never-started process is a no-op."""
    proc = TerminalProcess(working_dir=tmp_path)
    proc.stop()  # should not raise
    proc.stop()  # still safe


def test_info_disabled_payload_shape(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "project_os_cockpit.terminal.shutil.which", lambda name: None
    )
    info = TerminalProcess(working_dir=tmp_path).info()
    # Must NOT include url/command when disabled — JS branches on enabled.
    assert "url" not in info
    assert info["enabled"] is False
