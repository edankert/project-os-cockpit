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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .index import Index

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


#: The standing set's obligation — the one entry whose subject is **not a note
#: type** (TASK-0382).
#:
#: `architecture`, `glossary` and `reference` each declare `NONE` above, and
#: correctly: most `reference` notes are not standing documents at all (11 in
#: this repo's Reference group, 5 of them singletons), so making the TYPE owed
#: would count the wrong population. The subject here is a **manifest entry**,
#: which the type-keyed table has no way to express — so it is declared
#: separately rather than forced into a shape it does not fit.
#:
#: **Missing, ambiguous and stub count; stale does not.** The first three are
#: binary and one act clears each: write the document, delete the rival, fill
#: in the template. Staleness returns by the calendar — counting it is a badge
#: that re-arms itself forever, which is the permanent nag this project has
#: been bitten by twice (PHASE-015's close-out pill, `Doing · 44`). It still
#: MARKS the row; it just does not ask.
STANDING_OBLIGATION = Obligation(
    (), VIEW_INTENT, "Confirm",
    predicate="a manifest entry that is missing, ambiguous or holding its "
              "template. Staleness marks the row and does not count.",
)

#: What the standing obligation calls itself in a per-kind breakdown
#: (ISS-0133). It is the one obligation whose subject is not a note, so it has
#: no `note_type` to be keyed by and needs a name of its own.
STANDING_OBLIGATION_KIND = "standing document"

#: How a kind names itself when a badge counts it (ISS-0133), singular and
#: plural. Here rather than in the renderer because the obligation vocabulary
#: ships from the server and never from TypeScript (TASK-0357) — a plural rule
#: in the client is a second vocabulary, and `adr` -> `adrs` is exactly the
#: kind of thing it would get wrong on its own.
KIND_NOUNS: dict[str, tuple[str, str]] = {
    "adr": ("ADR", "ADRs"),
    "decision": ("decision", "decisions"),
    "design": ("design", "designs"),
    "requirement": ("requirement", "requirements"),
    "issue": ("issue", "issues"),
    "test": ("test", "tests"),
    "feature": ("feature", "features"),
    "change": ("change note", "change notes"),
    STANDING_OBLIGATION_KIND: ("standing document", "standing documents"),
}

#: Finding kinds from `standing.check` that the badge counts.
STANDING_OWED_KINDS: frozenset[str] = frozenset({"missing", "ambiguous", "stub"})


def standing_owed(docs_root: Any) -> int:
    """How many manifest entries are owed a person's attention."""
    from . import standing

    try:
        findings = standing.check(docs_root)
    except OSError:                      # pragma: no cover — unreadable tree
        return 0
    return sum(1 for f in findings if f.kind in STANDING_OWED_KINDS)


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


# ----- counting what is actually owed ---------------------------------------


def _is_owed(record: Any, ob: Obligation) -> bool:
    """Whether this note is currently owed under its type's declaration."""
    if not ob.owed:
        return False
    status = (record.status or "").strip().lower()

    if record.note_type == "change":
        # No review verdict — a GATE_BEARING_TYPE whose warnings become errors
        # on 2026-10-23. The historical cutoff is deliberately not applied
        # here; it is a parameter for whoever renders the badge (ISS-0128).
        return not str(record.frontmatter.get("review_verdict") or "").strip()

    if record.note_type == "feature":
        return str(record.frontmatter.get("acceptance") or "").strip().lower() == "requested"

    if record.note_type == "test":
        # Manual only: an automated test at `ready` waits on a runner, not a
        # person. `kind`/`level` carry that in this corpus.
        if status not in ob.states:
            return False
        blob = " ".join(
            str(record.frontmatter.get(k) or "") for k in ("kind", "level", "runner")
        ).lower()
        return "manual" in blob

    return status in ob.states


def counts_by_kind(index: "Index") -> dict[str, dict[str, int]]:
    """Owed items per view, **split by the kind that owes them** (ISS-0133).

    The badge has always shown a bare number, and the only explanation of it
    was a tooltip reading `N items here need a person` — the same sentence
    under every view, naming nothing. The kinds have been data since this
    module replaced a hand-written list of seven, so the breakdown costs one
    dict instead of one int and the surface stops having to say "items".
    """
    out: dict[str, dict[str, int]] = {v: {} for v in VIEWS}
    for path in index.paths():
        record = index.get(path)
        if record is None or not record.note_type:
            continue
        if record.rel_path.startswith("__templates__/"):
            continue
        ob = for_type(record.note_type)
        if ob is None or not ob.owed or not ob.view:
            continue
        if _is_owed(record, ob):
            bucket = out[ob.view]
            bucket[record.note_type] = bucket.get(record.note_type, 0) + 1
    # The one obligation whose subject is not a note (TASK-0382). Added here
    # rather than anywhere else so `badges_payload`'s total stays the sum of
    # what the badges show — a number that disagrees with itself on one screen
    # is the failure this module exists to prevent.
    standing = standing_owed(index.docs_root)
    if standing:
        bucket = out[STANDING_OBLIGATION.view]
        key = STANDING_OBLIGATION_KIND
        bucket[key] = bucket.get(key, 0) + standing
    return out


def counts(index: "Index") -> dict[str, int]:
    """Owed items per view — what each badge shows.

    Absent rather than zero is the renderer's job; this reports the truth and
    lets the surface decide what silence looks like.

    Derived from :func:`counts_by_kind` rather than counted separately: two
    passes over the same rule is how the total and the breakdown would come to
    disagree, which is the exact failure `badges_payload` exists to prevent.
    """
    return {view: sum(kinds.values()) for view, kinds in counts_by_kind(index).items()}


def badges_payload(index: "Index") -> dict[str, Any]:
    """The per-view counts plus the total, so a surface can assert on both.

    `total` is not decoration: ADR-0020 decision 3 says the badges must cover
    **every** kind, and a total that disagrees with the sum is how a kind goes
    missing without anyone noticing.
    """
    detail = counts_by_kind(index)
    per_view = {view: sum(kinds.values()) for view, kinds in detail.items()}
    return {
        "views": per_view,
        # Per view, `{kind: n}` for the kinds actually owed there right now
        # (ISS-0133) — so a badge can say `4 · requirements to approve` rather
        # than `4 items here need a person`, which was every view's tooltip.
        "breakdown": {view: kinds for view, kinds in detail.items() if kinds},
        # The verb each kind is owed, so the surface names the ACTION and does
        # not re-derive a vocabulary the registry already owns.
        "verbs": {
            note_type: ob.verb
            for note_type, ob in OBLIGATIONS.items() if ob.owed and ob.verb
        } | {STANDING_OBLIGATION_KIND: STANDING_OBLIGATION.verb},
        # `{kind: [singular, plural]}` — the noun the badge says. Shipped so
        # the renderer picks a string rather than owning a plural rule.
        "nouns": {kind: list(pair) for kind, pair in KIND_NOUNS.items()},
        "total": sum(per_view.values()),
        "kinds": sorted(owed_kinds()),
    }
