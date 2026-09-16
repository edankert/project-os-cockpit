"""Source-level guards for the Electron agent launch wrappers."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "desktop/src/ipc/agent-instrument.ts"

def test_codex_wrapper_preserves_terminal_scrollback():
    source = SOURCE.read_text(encoding="utf-8")

    assert "'codex'() { command codex --no-alt-screen -c" in source
    assert "'codex'() { command codex -c" not in source
    assert "codex-notify.sh" in source
    assert '"$@"' in source


def test_claude_wrapper_is_not_changed_by_codex_scrollback_fix():
    source = SOURCE.read_text(encoding="utf-8")

    assert "'claude'() { command claude --settings" in source
    assert "CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN" not in source
    assert "'claude'() { command claude --no-alt-screen" not in source
