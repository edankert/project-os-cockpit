"""Source-level guard for what a cockpit terminal does to `claude`.

Since FEAT-0156 the terminal wraps nothing: it puts the cockpit plugin on
CLAUDE_CODE_PLUGIN_DIRS, and the user's own `claude` (or their alias) runs.
The behaviour is tested in a real zsh by
desktop/tests/claude-plugin-shell.test.mjs; this guards the source against
the old wrapper or a scrollback flag coming back.
"""

from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "desktop/src/ipc/agent-instrument.ts"


def test_the_terminal_loads_the_plugin_and_does_not_wrap_claude():
    source = SOURCE.read_text(encoding="utf-8")

    assert "export CLAUDE_CODE_PLUGIN_DIRS=" in source
    assert "'claude'() {" not in source
    assert "unalias claude" not in source
    assert "claude-settings.json'), " not in source
    assert "CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN" not in source
