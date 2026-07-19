"""Parser-level tests for `cockpit signal <state>` (FEAT-0013 / TASK-0078).

`_post_json` is monkeypatched to capture the (base, path, body) the
CLI would send; the body shape is the contract the server-side
endpoint (TASK-0077) was tested against.
"""

from __future__ import annotations

from typing import Any

import pytest

from project_os_cockpit import cli as cli_module


@pytest.fixture
def capture_post(monkeypatch):
    """Replace `_post_json` so calls don't hit the network."""
    calls: list[tuple[str, str, dict]] = []

    def fake_post(base: str, path: str, body: dict) -> tuple[int, dict]:
        calls.append((base, path, body))
        return 200, {"ok": True}

    monkeypatch.setattr(cli_module, "_post_json", fake_post)
    # Stub discovery so the absence of a `.cockpit/url` doesn't bail.
    monkeypatch.setattr(cli_module, "_default_base_url", lambda: "http://127.0.0.1:8765")
    return calls


def test_signal_busy_minimal(capture_post):
    exit_code = cli_module.main(["signal", "busy"])
    assert exit_code == 0
    assert capture_post == [(
        "http://127.0.0.1:8765",
        "/api/cockpit/agent-state",
        {"state": "busy"},
    )]


def test_signal_busy_with_target_and_agent(capture_post):
    cli_module.main([
        "signal", "busy", "--target", "FEAT-0013", "--agent", "claude",
    ])
    base, path, body = capture_post[0]
    assert body == {
        "state": "busy", "target": "FEAT-0013", "agent": "claude",
    }


def test_signal_waiting_with_message(capture_post):
    cli_module.main([
        "signal", "waiting", "--message", "review my PR",
    ])
    _base, _path, body = capture_post[0]
    assert body == {"state": "waiting", "message": "review my PR"}


def test_signal_done_minimal(capture_post):
    cli_module.main(["signal", "done"])
    _base, _path, body = capture_post[0]
    assert body == {"state": "done"}


def test_signal_error_with_message(capture_post):
    cli_module.main([
        "signal", "error", "--message", "merge conflict in X",
    ])
    _base, _path, body = capture_post[0]
    assert body == {"state": "error", "message": "merge conflict in X"}


def test_signal_idle_resets_state(capture_post):
    cli_module.main(["signal", "idle"])
    _base, _path, body = capture_post[0]
    assert body == {"state": "idle"}


def test_signal_rejects_invalid_state(monkeypatch, capsys):
    """Argparse should reject any state outside the documented set."""
    with pytest.raises(SystemExit):
        cli_module.main(["signal", "ascending"])
    err = capsys.readouterr().err
    assert "invalid choice" in err.lower() or "ascending" in err.lower()


def test_signal_propagates_server_error(monkeypatch, capsys):
    """When the server returns an error, the CLI exits non-zero with
    the message on stderr."""
    def fake_post(base, path, body):
        return 400, {"ok": False, "error": "missing 'state'"}
    monkeypatch.setattr(cli_module, "_post_json", fake_post)
    monkeypatch.setattr(cli_module, "_default_base_url",
                        lambda: "http://127.0.0.1:8765")
    exit_code = cli_module.main(["signal", "busy"])
    assert exit_code == 1
    assert "missing 'state'" in capsys.readouterr().err


def test_signal_uses_cockpit_url_override(capture_post):
    """`--cockpit-url` should override `_default_base_url`."""
    cli_module.main([
        "--cockpit-url", "http://otherhost:9999",
        "signal", "busy",
    ])
    base, _path, _body = capture_post[0]
    assert base == "http://otherhost:9999"
