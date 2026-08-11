"""The agent roster is data, not a literal pair (ISS-0095).

`agents.py` already did the hard part — FEAT-0019 collapsed nine restatements
into one table — so this is a small, well-prepared gap rather than a tangle.

It matters more after ADR-0009: *the principal is a role, not a person*, and
the same argument applies one step down. **The worker is a role too.** A
standing worker that can only ever be one vendor is a loop with a single point
of vendor failure, and it forecloses the cheapest quality mechanism available —
a second opinion from a different model on the same item, which ADR-0013
already blesses for review.
"""

from __future__ import annotations

from project_os_cockpit import agents


def test_a_third_agent_needs_one_entry_and_nothing_else() -> None:
    """The issue's own evidence-it-is-fixed."""
    extended = agents.extend([
        {"id": "cursor", "label": "Cursor", "command": "cursor", "instrumented": False},
    ])
    ids = [a["id"] for a in extended]
    assert ids == ["claude", "codex", "cursor"], ids
    # And everything that reads the table keeps working off it.
    assert agents.is_dispatchable("claude") is True
    assert agents.is_dispatchable("nothing") is False


def test_a_half_declared_agent_is_dropped_not_shown() -> None:
    """A dispatch that fails *after* the human committed to it is worse than an
    agent that never appeared."""
    for broken in (
        {"id": "x", "label": "", "command": "x"},
        {"id": "", "label": "X", "command": "x"},
        {"id": "x", "label": "X", "command": ""},
        {"not": "a spec"},
        "not a dict",
    ):
        ids = [a["id"] for a in agents.extend([broken])]
        assert ids == ["claude", "codex"], (broken, ids)


def test_a_repo_may_replace_a_built_in_row() -> None:
    """So a project can change how `claude` is launched without forking the
    table — which is what a fork would become the moment it existed."""
    extended = agents.extend([
        {"id": "claude", "label": "Claude (fast)", "command": "claude",
         "instrumented": True, "args": ["--fast"]},
    ])
    claude = next(a for a in extended if a["id"] == "claude")
    assert claude["label"] == "Claude (fast)"
    assert claude["args"] == ("--fast",)
    assert len(extended) == 2, "replacing a row added one instead"


def test_optional_hints_stay_optional() -> None:
    """`args` and `role` are hints; nothing keys behaviour off `role`."""
    plain = agents.extend([{"id": "grok", "label": "Grok", "command": "grok"}])
    grok = next(a for a in plain if a["id"] == "grok")
    assert "args" not in grok and "role" not in grok
    assert grok["instrumented"] is False, "instrumentation defaulted to true"


def test_the_built_in_table_is_untouched_by_extension() -> None:
    """`extend` must not mutate the module-level tuple — a repo's config would
    otherwise leak into every workspace in the process."""
    before = [dict(a) for a in agents.AGENTS]
    agents.extend([{"id": "cursor", "label": "Cursor", "command": "cursor"}])
    assert [dict(a) for a in agents.AGENTS] == before
