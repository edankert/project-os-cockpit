"""Agent vocabulary parity (ISS-0032).

`tests/test_status_vocabulary.py` exists because the status vocabulary was
restated across eight surfaces and drifted (ISS-0023). This is the same guard
for the agent vocabulary, which had drifted across nine.

The distinction every test here turns on:

  DISPATCHABLE is closed  -- `agents.AGENTS` says which agents the cockpit can
                             launch. One declaration, served to the renderer.
  RECORDABLE is open      -- any string may appear in a session record or a
                             signal. Someone ran an agent in an external
                             terminal; that is history, not bad data.

Collapsing those two is what produced the bug: the queue validated *records*
against the *dispatchable* set and silently discarded anything else.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from project_os_cockpit import agents

ROOT = pathlib.Path(__file__).resolve().parents[1]
RENDERER = ROOT / "desktop" / "src" / "renderer" / "renderer.ts"
MAIN = ROOT / "desktop" / "src" / "main.ts"
QUEUE = ROOT / "desktop" / "src" / "ipc" / "dispatch-queue.ts"


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def _code_only(text: str) -> str:
    """Strip `//` line comments and `/* */` blocks.

    Every check below looks for a *pattern in the code*. The comments in these
    files quote the patterns they replaced -- deliberately, so a later reader
    knows what the shape used to be -- and a check that reads prose would fire
    on the explanation of the fix rather than on the defect. That is not a
    hypothetical: the first version of `test_queue_validator_does_not_check_membership`
    failed against the comment describing the bug it verifies is gone.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in text.splitlines())


# ---- the registry itself -------------------------------------------------

def test_registry_is_the_only_python_declaration() -> None:
    """`cli.py` must read its choices from the registry, not restate them."""
    cli = _read(ROOT / "src" / "project_os_cockpit" / "cli.py")
    assert 'choices=["claude", "codex"]' not in cli
    assert "agents.AGENT_IDS" in cli


def test_ids_are_unique_and_lowercase() -> None:
    ids = [a["id"] for a in agents.AGENTS]
    assert ids == [i.lower() for i in ids]
    assert len(ids) == len(set(ids))
    assert agents.DEFAULT_AGENT in ids


def test_every_agent_carries_a_launch_command() -> None:
    """An agent with no command cannot be dispatched, so it does not belong
    in a registry of dispatchable agents."""
    for spec in agents.AGENTS:
        assert spec["command"], spec["id"]
        assert spec["label"], spec["id"]


# ---- dispatchable is closed ----------------------------------------------

def test_unknown_agent_does_not_resolve_to_a_sibling() -> None:
    """The ISS-0032 defect, asserted directly: an unrecognised agent must not
    come back as `claude`."""
    assert agents.resolve_dispatch_agent("kimi") is None
    assert agents.resolve_dispatch_agent("") is None
    assert agents.resolve_dispatch_agent(None) is None
    assert agents.resolve_dispatch_agent("claude") == "claude"
    assert agents.resolve_dispatch_agent("  CODEX ") == "codex"


def test_is_dispatchable_matches_the_registry() -> None:
    for spec in agents.AGENTS:
        assert agents.is_dispatchable(spec["id"])
    assert not agents.is_dispatchable("kimi")
    assert not agents.is_dispatchable(None)


# ---- recordable is open --------------------------------------------------

def test_unknown_agent_renders_as_itself() -> None:
    """A recorded agent the cockpit cannot launch must display under its own
    name. Showing it as another agent misattributes the work."""
    assert agents.label_for("kimi") == "kimi"
    assert agents.label_for("claude") == "Claude Code"
    assert agents.label_for(None) == "unknown"


def test_ingestion_paths_do_not_gate_on_dispatchability() -> None:
    """`agent_hooks` and `server` preserve any agent string. They were already
    correct before ISS-0032 and the fix must not 'tidy' them into the closed
    set -- that would discard real external-terminal history."""
    hooks = _read(ROOT / "src" / "project_os_cockpit" / "agent_hooks.py")
    assert 'agent = agent if isinstance(agent, str) and agent else "claude"' in hooks
    for src in ("agent_hooks.py", "server.py"):
        text = _read(ROOT / "src" / "project_os_cockpit" / src)
        assert "is_dispatchable" not in text, (
            "%s gates a recorded agent on dispatchability; recordable is open" % src
        )


# ---- the TypeScript surfaces hold no membership of their own -------------

@pytest.mark.parametrize("path", [RENDERER, MAIN, QUEUE])
def test_no_closed_agent_union(path: pathlib.Path) -> None:
    """No surface may declare the agent set as a union type."""
    text = _code_only(_read(path))
    assert not re.search(r"'claude'\s*\|\s*'codex'", text), (
        "%s declares a closed agent union; membership belongs to agents.py "
        "and reaches the renderer via /api/cockpit/agents" % path.name
    )


@pytest.mark.parametrize("path", [RENDERER, MAIN])
def test_no_agent_coercion(path: pathlib.Path) -> None:
    """The ISS-0032 coercions: `x === 'codex' ? 'codex' : 'claude'` relabels an
    unrecognised agent instead of rejecting it."""
    text = _code_only(_read(path))
    coercion = re.compile(
        r"===\s*'codex'\s*\?\s*'codex'(?:\s+as\s+const)?\s*:\s*'claude'")
    hits = [m.start() for m in coercion.finditer(text)]
    assert not hits, (
        "%s coerces an unrecognised agent to 'claude' at offset(s) %s" %
        (path.name, hits))


def test_queue_validator_does_not_check_membership() -> None:
    """The real ISS-0032 defect. The queue validates persisted items; if it
    also checks membership, a third agent's queued work is discarded on
    restart -- silently, and against FEAT-0025's promise."""
    text = _code_only(_read(QUEUE))
    assert "it.agent === 'claude'" not in text
    assert "typeof it.agent === 'string'" in text


def test_renderer_resolves_through_the_registry() -> None:
    """The renderer must ask the served registry, not its own list."""
    text = _code_only(_read(RENDERER))
    assert "/api/cockpit/agents" in text
    assert "function resolveDispatchAgent" in text
    # loadDispatchAgent must not hardcode a fallback member.
    m = re.search(r"function loadDispatchAgent\(\)[^}]*\}[^}]*\}", text, re.S)
    assert m, "loadDispatchAgent not found"
    assert "'codex'" not in m.group(0), (
        "loadDispatchAgent still names a specific agent; it should resolve "
        "through the registry and fall back to the served default")


def test_main_builds_the_menu_from_the_payload() -> None:
    """The agent radio menu must come from the registry, so adding an agent is
    one entry in agents.py rather than an edit in the main process too."""
    text = _code_only(_read(MAIN))
    assert "menuAgents" in text
    assert "label: 'Claude Code', type: 'radio'" not in text, (
        "main.ts still hardcodes agent radio entries")


# ---- adequacy: the guard must be able to fail ---------------------------

def test_parity_checks_detect_a_regression(tmp_path: pathlib.Path) -> None:
    """A test that cannot fail does not guard (QUALITY.md, 'Test adequacy').

    Re-introduce each defect into a copy of the real source and assert the
    corresponding check would fire. Without this, the checks above are just
    assertions that today's file happens to look a certain way.
    """
    coercion = re.compile(
        r"===\s*'codex'\s*\?\s*'codex'(?:\s+as\s+const)?\s*:\s*'claude'")

    # 1. the coercion, in both the plain and `as const` spellings
    for spelling in ("ev.agent === 'codex' ? 'codex' : 'claude'",
                     "ev.agent === 'codex' ? 'codex' as const : 'claude' as const"):
        assert coercion.search(spelling), spelling
    assert not coercion.search("ev.agent === 'codex' ? 'codex' as const\n"
                               ": ev.agent === 'claude' ? 'claude' as const : undefined"), (
        "the coercion check must NOT flag the correct two-line narrowing -- "
        "mistaking one for the other is what made ISS-0032's first diagnosis wrong")

    # 2. the closed union
    union = re.compile(r"'claude'\s*\|\s*'codex'")
    assert union.search("  agent: 'claude' | 'codex';")
    assert not union.search("  agent: string;")

    # 3. the queue membership check
    reverted = _code_only(_read(QUEUE)).replace(
        "typeof it.agent === 'string' && it.agent.length > 0",
        "(it.agent === 'claude' || it.agent === 'codex')")
    assert "it.agent === 'claude'" in reverted
