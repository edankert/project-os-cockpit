"""Source-level guard for the Claude launch wrapper."""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "desktop/src/ipc/agent-instrument.ts"

def test_claude_wrapper_is_not_changed_by_codex_scrollback_fix():
    source = SOURCE.read_text(encoding="utf-8")

    assert "'claude'() { command claude --settings" in source
    assert "CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN" not in source
    assert "'claude'() { command claude --no-alt-screen" not in source
