"""What the record owes a person, enumerated **by note type** (TASK-0369).

ADR-0020: *an obligation surfaces in the view that owns its subject*, and the
count lives on the view button. That is only enforceable if the kinds exist as
data — so this is the data, and it is the single source. `GET /api/notes/actions`
and the per-view badges both read it; no renderer restates it.

**By type, not by obligation kind, and that inversion is the whole design.**
The first cut of this module listed seven kinds by name, drawn from the review
desk's contents. It was wrong three times in one day — `change` (116 notes, 76
unreviewed), `release`, then `risk`/`workflow`/`phase` (40 between them). Each
was found by Edwin asking "what about X?", never by anything failing, because a
list written from one surface cannot know what was never on it.

Enumerating by type inverts the burden: **the corpus supplies the checklist.**
A type present in the notes with no declaration is a test failure rather than
something somebody has to notice.

**`NONE` is explicit and carries its reason.** `task` (381 notes) and `plan`
(52) genuinely owe nothing — correct, load-bearing, and indistinguishable from
an omission when unwritten. That is what makes the completeness test mean
something instead of being a formality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

#: The views an obligation may be owned by. One type, one view — otherwise the
#: badges count it twice or neither.
VIEW_OVERVIEW = "overview"
VIEW_INTENT = "intent"
VIEW_FEATURES = "features"
VIEW_ISSUES = "issues"
VIEW_TESTS = "tests"

VIEWS: frozenset[str] = frozenset({
    VIEW_OVERVIEW, VIEW_INTENT, VIEW_FEATURES, VIEW_ISSUES, VIEW_TESTS,
})


@dataclass(frozen=True)
class Obligation:
    """One kind of owed judgment, or an explicit absence of one."""

    #: Statuses that make a note of this type owed. Empty means "not driven by
    #: status" — see `predicate` — or, with `owed=False`, nothing at all.
    states: tuple[str, ...] = ()
    view: str = ""
    verb: str = ""
    owed: bool = True
    #: Why this type owes nothing. **Required** when `owed` is False: an
    #: unexplained absence is what an omission looks like from the outside.
    reason: str = ""
    #: Set when the obligation is not a plain status match, so a reader knows
    #: the predicate lives elsewhere rather than assuming this is the whole rule.
    predicate: str = ""


def NONE(reason: str, view: str = "") -> Obligation:  # noqa: N802 — reads as a literal
    return Obligation(owed=False, reason=reason, view=view)


#: Every note type in the corpus. A type here with no entry fails a test.
OBLIGATIONS: dict[str, Obligation] = {
    # ---- owed ----------------------------------------------------------
    "adr": Obligation(("proposed",), VIEW_INTENT, "Decide"),
    "decision": Obligation(("proposed",), VIEW_INTENT, "Decide"),
    "design": Obligation(("proposed",), VIEW_INTENT, "Accept"),
    "requirement": Obligation(("draft", "proposed"), VIEW_FEATURES, "Approve"),
    "issue": Obligation(("triage",), VIEW_ISSUES, "Triage"),
    "test": Obligation(
        ("ready",), VIEW_TESTS, "Run",
        predicate="manual tests only — an automated test at `ready` waits on a "
                  "runner, not on a person",
    ),
    "feature": Obligation(
        (), VIEW_FEATURES, "Accept",
        predicate="`acceptance: requested` in frontmatter, not a status "
                  "(DES-0006's opt-in gate)",
    ),
    "change": Obligation(
        (), VIEW_OVERVIEW, "Review",
        predicate="no `review_verdict`; a GATE_BEARING_TYPE whose warnings "
                  "become errors on 2026-10-23. 76 of 116 here — whether the "
                  "historical ones count is a cutoff parameter, not a constant",
    ),

    # ---- owed nothing, and why -----------------------------------------
    "task": NONE(
        "agent-owned end to end: backlog -> doing -> done carries no human "
        "judgment. STATUSES.md's ownership table assigns every task transition "
        "to the agent.",
        VIEW_FEATURES,
    ),
    "plan": NONE(
        "a plan's status follows its parent feature and is advanced at "
        "close-out (STATUSES.md). `draft` on a plan means the feature has not "
        "started, not that anyone owes it a decision — which is why plans were "
        "removed from the review desk queue on 2026-07-26.",
        VIEW_FEATURES,
    ),
    "phase": NONE(
        "closing a phase is a PROCEDURE that follows the work, not a judgment "
        "somebody is holding up: re-home the children, tick the exit criteria "
        "with evidence, set `superseded_by`, update PHASES.md and the snapshot. "
        "There is no single transition an actuator could offer, and "
        "`phase_close_blockers()` already reports when closing is POSSIBLE — a "
        "gate, not a debt. The Overview's `unclosed` pill stays as a mark. "
        "(Edwin, 2026-08-10 — ISS-0128.)",
        VIEW_FEATURES,
    ),
    "risk": NONE(
        "`open` is a risk's resting state. A risk is a hazard the project has "
        "decided to CARRY, and carrying one is not a debt — it may never "
        "arrive. All six here have sat at `open` since they were written, and "
        "that is correct rather than neglected. (Edwin, 2026-08-10 — ISS-0128.)",
        VIEW_INTENT,
    ),
    "workflow": NONE(
        "workflows document the TOOLING, not this project's lifecycle. "
        "WF-0001..0003 ship with the template under `group:maintainers` and "
        "describe `project-derive`, `sync-project-os.sh` and `snapshot-sync`. "
        "This repo received them; it does not curate them, so their `draft` is "
        "not a claim about anything it owes. (Edwin, 2026-08-10 — ISS-0128.)",
        VIEW_INTENT,
    ),
    "release": NONE(
        "the release GATE is a test obligation, not a release one — its "
        "subject is an unchecked Tier 1/2 test, so it surfaces in Tests "
        "(ADR-0020 amendment 11). The Overview owns the release RECORD.",
        VIEW_OVERVIEW,
    ),
    "reference": NONE(
        "a standing document has no lifecycle. Its state is freshness, which "
        "FEAT-0091's manifest reports as missing / ambiguous / stub / stale — "
        "a warning, never a build error.",
        VIEW_INTENT,
    ),
    "architecture": NONE(
        "a standing document: one per project, no lifecycle, written to be "
        "read. Its state is freshness — ISS-0125 measured this class at 94% "
        "stale fleet-wide — and freshness warns rather than owing.",
        VIEW_INTENT,
    ),
    "glossary": NONE(
        "a standing document: one per project, no lifecycle. A definition is "
        "true or out of date, never owed to somebody; FEAT-0091's manifest "
        "reports the second as a warning.",
        VIEW_INTENT,
    ),
    "dashboard": NONE(
        "removed from this corpus (TASK-0383) — an Obsidian artifact whose "
        "`.base` embeds were all dead. Declared so the type does not reappear "
        "undeclared if a repo still carries one.",
    ),
}


def declared_types() -> frozenset[str]:
    return frozenset(OBLIGATIONS)


def for_type(note_type: str | None) -> Obligation | None:
    return OBLIGATIONS.get((note_type or "").strip().lower())


def owed_kinds() -> dict[str, Obligation]:
    """Only the types that owe something — what the badges count."""
    return {k: v for k, v in OBLIGATIONS.items() if v.owed}


def views_owed() -> dict[str, list[str]]:
    """Which types each view is answerable for."""
    out: dict[str, list[str]] = {v: [] for v in sorted(VIEWS)}
    for note_type, ob in OBLIGATIONS.items():
        if ob.owed and ob.view:
            out[ob.view].append(note_type)
    return out


def payload() -> dict[str, Any]:
    """The registry as data, for renderers that draw what they are sent."""
    return {
        "views": sorted(VIEWS),
        "kinds": [
            {
                "type": note_type,
                "states": list(ob.states),
                "view": ob.view,
                "verb": ob.verb,
                "predicate": ob.predicate,
            }
            for note_type, ob in sorted(OBLIGATIONS.items()) if ob.owed
        ],
        "none": [
            {"type": note_type, "reason": ob.reason, "view": ob.view}
            for note_type, ob in sorted(OBLIGATIONS.items()) if not ob.owed
        ],
    }
