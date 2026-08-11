"""Guarded note write-back for the review desk (FEAT-0041).

Two mutations, both narrow by construction:

* :func:`stamp_review` — writes the three independent-review fields
  (``reviewed_by`` / ``review_date`` / ``review_verdict``), optionally
  with a guarded status transition.
* :func:`stamp_test_run` — writes a manual test's outcome (``status`` +
  ``last_run``) and appends a run log under ``## Runs``.

Everything else about a note is off-limits. That is a deliberate design
constraint rather than an implementation shortcut: PHASE-007 drew the
line at "the cockpit is a viewer", and ADR-0007 crosses it only far
enough to record a decision a human made in the UI. The allow-list below
is what keeps that crossing honest, and the tests assert it.

Hardening (TASK-0207 DoD, folded in from the preflight risk scan rather
than filed as a separate RISK):

* **Field allow-list** — a payload naming any other frontmatter key is
  rejected outright; the writer never merges caller-supplied dicts.
* **Guarded transitions** — a status must exist in ``statuses.py`` and be
  one of the transitions this module permits; anything else is a 4xx with
  nothing written.
* **Path canonicalisation** — targets resolve through the index and must
  land inside ``docs_root`` (the TASK-0174 case-canonicalisation
  precedent), so no traversal reaches the filesystem.
* **Concurrency** — an ``mtime`` precondition from the reader means a
  note edited underneath the reviewer fails loudly instead of silently
  clobbering the newer text.
* **Snapshot untouched** — ADR-0009: notes are the authored source, and
  ``sync-snapshot.py`` propagates at pre-commit. This module never edits
  SNAPSHOT.yaml.

The endpoints that call this refuse non-loopback callers — a per-request
peer-address check on the shared 0.0.0.0 socket, not a separate bind. The
distinction matters: the render server binds 0.0.0.0 so a tablet can read
the notes, and the guard is what keeps mutation off that surface (the
RISK-0001 threat model; the terminal endpoint gets a real second bind
because it can afford one).
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import Any

from . import statuses
from .index import Index

#: The only frontmatter keys this module may create or overwrite.
REVIEW_FIELDS: frozenset[str] = frozenset({
    "reviewed_by", "review_date", "review_verdict",
})
TEST_RUN_FIELDS: frozenset[str] = frozenset({
    "status", "last_run", "last_verified",
})
#: `updated` is written by both paths — every note edit touches it, and
#: leaving it stale would make the corpus lie about its own freshness.
#: It is in the allow-list because it IS written, not as an exception.
BOOKKEEPING_FIELDS: frozenset[str] = frozenset({"updated"})

#: Fields a design review verdict may touch. `design_revision` records WHICH
#: revision was accepted — without it an approval given to v3 silently launders
#: v6, which is the one way a design review can be worse than none.
DESIGN_REVIEW_FIELDS: frozenset[str] = frozenset({
    "reviewed_by", "review_date", "review_verdict", "design_revision",
})

#: Fields a design capture may touch. Nothing about status or review — a
#: capture records that a revision happened, never that it was any good.
DESIGN_CAPTURE_FIELDS: frozenset[str] = frozenset({"updated"})

ALLOWED_FIELDS: frozenset[str] = (
    REVIEW_FIELDS | TEST_RUN_FIELDS | BOOKKEEPING_FIELDS | DESIGN_REVIEW_FIELDS
)

#: Request-body keys each endpoint accepts. Kept here beside the field
#: allow-list so the two cannot drift — an earlier cut duplicated these
#: as literals in `server.py`, which meant the exported allow-list was
#: decorative (independent review, 2026-07-26).
REVIEW_REQUEST_KEYS: frozenset[str] = frozenset({
    "id", "reviewer", "verdict", "status", "mtime",
})
TEST_RUN_REQUEST_KEYS: frozenset[str] = frozenset({
    "id", "outcome", "steps", "runner", "mtime", "aborted",
})
DECIDE_REQUEST_KEYS: frozenset[str] = frozenset({
    "id", "reviewer", "accept", "mtime",
})

#: Plan acceptance must never be mistaken for close-out independent
#: review. Close-out writes `approved` (QUALITY.md); the desk writes
#: `plan-accepted`, so the close-out gate cannot be satisfied by having
#: had one's plan approved — recorded as an ADR-0007 consequence.
PLAN_ACCEPTED_VERDICT = "plan-accepted"
PLAN_REJECTED_VERDICT = "plan-rejected"
DESK_VERDICTS: frozenset[str] = frozenset({
    PLAN_ACCEPTED_VERDICT, PLAN_REJECTED_VERDICT,
})
CLOSE_OUT_VERDICTS: frozenset[str] = frozenset({"approved", "changes-requested"})

#: Note types whose `review_verdict` the *close-out* gate reads
#: (ADR-0011 checks tests and changes for an independent-review stamp).
#: The desk must never write a verdict onto one of these: the validator
#: accepts any non-`changes-requested` value, so a plan stamp landing on
#: a TST or CHG would silence a gate it never satisfied. Refusing by type
#: closes the hole that refusing the string `approved` only narrowed
#: (independent review, 2026-07-26).
GATE_BEARING_TYPES: frozenset[str] = frozenset({"test", "change"})

#: Status transitions this module may perform. Rejecting a proposal set
#: is the only status write the review path needs; the runner writes test
#: outcomes. Everything else stays a human edit in the note.
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "review": frozenset({"cancelled"}),
    "test-run": frozenset({"passing", "failing"}),
}

#: Deciding a *lone* queued note is a real lifecycle move, and the move
#: differs by type — which is why the set-review path's single `cancelled`
#: transition left ADR-0007 and every draft requirement un-actionable
#: (reported 2026-07-26). Each entry is (accept, decline), drawn from that
#: type's own vocabulary in STATUSES.md:
#:
#: * ADR — `proposed → accepted`. There is no "reject": STATUSES.md is
#:   explicit that a decision not taken is *deleted or superseded*, never
#:   marked rejected, because a rejected proposal worth keeping is worth
#:   recording as the alternative it lost to.
#: * Requirement — `draft → approved`, or `cancelled` if it will not be built.
#: The design statuses this module knows how to reason about. Used for ONE
#: thing: failing closed on a status it has never seen, which otherwise got
#: silently demoted.
#:
#: This was a rank table until independent review proved the ranks were dead —
#: replacing the whole backwards comparison with `False` left all 496 tests
#: passing, because accept's candidate is `accepted` and every status ranking
#: above it is in `_DESIGN_SETTLED`, which is checked first. The comment said
#: the ranks refused a move that would rewrite history; `_DESIGN_SETTLED`
#: refuses it. Keeping ordering nobody consults, under a comment claiming it
#: guards something, is the exact defect this review kept finding elsewhere.
_DESIGN_KNOWN_STATUSES: frozenset[str] = frozenset({
    "draft", "proposed", "accepted", "implemented", "superseded", "cancelled",
})

#: Statuses a review verdict must never move a design out of. Rank alone
#: cannot express this: `cancelled` ranks ABOVE `implemented`, so cancelling a
#: shipped design reads as a FORWARD move (independent review round 3). A
#: design that shipped cannot be un-shipped by a verdict — deciding to replace
#: it is a new design or an issue, not a status flip on the old one.
_DESIGN_SETTLED: frozenset[str] = frozenset({
    "implemented", "superseded", "cancelled",
})

#: The human-owned transition table, as data (TASK-0278).
#:
#: DES-0005's matrix: ``(type, from-status) -> the actions a human may take``.
#: Every entry is a judgment that is *inherently the asker's* — approving a
#: requirement, accepting a design, triaging an issue. Deliberately absent is
#: every agent-owned transition: close-out statuses (``done``, ``fixed``,
#: ``merged``, ``implemented``), anything test-gated, anything the validator
#: computes. REQ-0026 is the contract, and this table is what makes it
#: enforceable rather than a convention — the refusal is the server's, so no
#: display bug can widen it.
#:
#: Removing an entry removes the action from every surface with no renderer
#: change. That is the point: the vocabulary exists once (the ISS-0023 rule),
#: and `GET /api/notes/actions` is how a renderer learns it.
HUMAN_TRANSITIONS: dict[str, dict[str, tuple[tuple[str, str], ...]]] = {
    "requirement": {
        "draft":    (("Approve", "approved"), ("Decline", "cancelled")),
        "proposed": (("Approve", "approved"), ("Decline", "cancelled")),
    },
    "adr": {
        "proposed": (("Accept", "accepted"), ("Supersede", "superseded")),
    },
    "decision": {
        "proposed": (("Accept", "accepted"), ("Supersede", "superseded")),
    },
    # A design accepted is not yet built — `implemented` is what shipping
    # means. Declining writes `cancelled`, not `superseded`: superseded means a
    # LATER design replaced it, a different fact about the future.
    "design": {
        "proposed": (("Accept", "accepted"), ("Decline", "cancelled")),
    },
    # `Defer` is the third verb ADR-0020 found missing. Measured across the
    # fleet on 2026-08-10: 39 issues sit at `triage` with a median age of 56
    # days, and the only offers were accept or decline — so "real, but not
    # now" had nowhere to go, which is a fair part of why they sit. `deferred`
    # was already legal in STATUSES.md and already has a mark in DES-0004
    # (hollow + strike, *parked, still wanted*).
    "issue": {
        "triage": (
            ("Accept", "open"),
            ("Defer", "deferred"),
            ("Decline", "declined"),
        ),
    },
}

#: Actions whose consequence is terminal, so a surface asks once before
#: performing them. Forward moves need no confirmation: reversing an approve
#: is itself a recorded action, so the cost of a slip is a line of history.
CONFIRM_ACTIONS: frozenset[str] = frozenset({"Decline", "Supersede"})

TRANSITION_REQUEST_KEYS: frozenset[str] = frozenset(
    {"id", "to", "actor", "mtime", "severity"}
)

#: Severities an accept-as may record. Same list the issue template documents.
SEVERITIES: frozenset[str] = frozenset({"critical", "high", "medium", "low"})


#: Types whose verdict must NOT go through the generic transition path, and
#: the endpoint that owns each one instead (TASK-0375).
#:
#: **This is ISS-0056's hazard, and the generic table re-opened it.** A design
#: accepted through `/api/notes/transition` gets `status: accepted` and no
#: `design_revision` — so an approval given to revision 3 silently covers
#: revision 6, which is the one way a design review is worse than no review at
#: all. Rejection is worse still: it would write `cancelled` onto a design that
#: may already be `implemented`.
#:
#: TASK-0218 built `/api/design/verdict` precisely to make a verdict name the
#: revision it judged, and validates that revision against real git history.
#: The actuator row still offers the buttons — the vocabulary stays in this
#: table — but they carry the endpoint that has to serve them.
#: The value is the route itself, not a nickname for it: the renderer posts to
#: what it is sent, and the refusal message below can name the real URL. A
#: nickname needed translating on both sides, and got it wrong on the first
#: try — the message said `/api/design-verdict`, an endpoint that does not
#: exist, which is the kind of error a person reads and then cannot act on.
VERDICT_ENDPOINTS: dict[str, str] = {
    "design": "/api/design/verdict",
}

#: What each verdict-routed action means to its endpoint, keyed by
#: (type, target status). The endpoint speaks `verdict` + `accept`, not
#: statuses, so somebody has to translate — and it is this module, beside the
#: table the verbs come from. A renderer inferring `accept` from the button's
#: tone (or its label) is the status vocabulary leaking into TypeScript one
#: field at a time, which is ISS-0023 in a new costume.
VERDICT_SEMANTICS: dict[tuple[str, str], dict[str, Any]] = {
    ("design", "accepted"): {"verdict": "approved", "accept": True},
    ("design", "cancelled"): {"verdict": "changes-requested", "accept": False},
}


def legal_actions(
    note_type: str | None,
    status: str | None,
    *,
    caller: str = "",
    policy: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """What a human may do to a note in this state, for `GET /api/notes/actions`.

    Returns the empty list when nothing is offered, which is the common case:
    most notes at most times owe nobody a decision.

    **`caller` and `policy` are REQ-0030's first layer** (TASK-0327). A human
    caller sees the table as written. A *delegate* — any `agent:*` — sees only
    what an **approved** delegation policy names, so an out-of-policy action is
    never offered. The second layer is the write path, which checks again,
    because a display bug must not be able to widen authority: exactly the
    REQ-0026 pattern, one level up.

    A caller of `""` is treated as human. That keeps every existing call site
    working unchanged — and it is safe because a delegate is identified by
    saying so, while the guard that actually stops a delegate lives at the
    write path where the identity is checked rather than assumed.

    An action may name an `endpoint`. Absent means the generic transition path;
    present means that path will refuse it — see :data:`VERDICT_ENDPOINTS`. The
    renderer reads the field rather than the type, so the one place that knows
    designs are special is this module.
    """
    kind = (note_type or "").strip().lower()
    entries = HUMAN_TRANSITIONS.get(kind, {})
    offered = entries.get((status or "").strip().lower(), ())
    endpoint = VERDICT_ENDPOINTS.get(kind, "")
    actions = [
        {
            "verb": verb,
            "to": to_status,
            "confirm": verb in CONFIRM_ACTIONS,
            "disabled": False,
            "reason": "",
            "endpoint": endpoint,
            **(VERDICT_SEMANTICS.get((kind, to_status), {}) if endpoint else {}),
        }
        for verb, to_status in offered
    ]

    # **REQ-0030's first layer** (TASK-0327): a delegate is offered only what an
    # approved policy names. A human sees the table as written.
    #
    # The second layer is the write path, which checks the same policy again —
    # because a display bug must not be able to widen authority. That is
    # REQ-0026's pattern applied one level up, and the reason this filter is
    # not the guard: it is the *offer*.
    who = (caller or "").strip().lower()
    if not who.startswith("agent:"):
        return actions
    from . import delegation as _delegation
    return [
        action for action in actions
        if _delegation.permits(policy or {}, f"{action['verb']} {kind}", who)
    ]


#: The two shapes a criterion may be resolved into (TASK-0279). Both are what
#: `validate_docs_bundled.CHECKED_RE` / `RECONCILED_RE` parse — written here as
#: format strings so the writer and the validator cannot drift into disagreeing
#: about a line only one of them produces.
TICK_TEMPLATE = "- [x] {text} — evidence: {evidence} ({actor}, {date})"
RECONCILE_TEMPLATE = "- [~] {text} — {reason} ({actor}, {date})"

TICK_REQUEST_KEYS: frozenset[str] = frozenset(
    {"id", "criterion", "evidence", "reason", "actor", "mtime"}
)

_BOX_RE = re.compile(r"^(\s*[-*+]\s*)\[([ xX~])\]\s*(.*)$")


def _criterion_text(line: str) -> str | None:
    """The prose of a checkbox line, stripped of its box and any resolution
    already appended. ``None`` when the line is not a checkbox at all."""
    m = _BOX_RE.match(line)
    if not m:
        return None
    box = m.group(2)
    body = m.group(3).strip()
    # A RESOLVED criterion carries its evidence or reason after an em dash;
    # strip that so re-resolving matches the criterion rather than nesting.
    #
    # Keyed on the box, not on the presence of an em dash. An earlier cut
    # split on " — " unconditionally and so could not address any criterion
    # that contains one — REQ-0027's fourth reads "…re-renders its surfaces —
    # no optimistic UI…", and was unreachable. An unticked box has no
    # resolution to strip, so there is nothing to guess at.
    if box in ("x", "X", "~"):
        for sep in (" — evidence:", " — "):
            if sep in body:
                body = body.split(sep, 1)[0].strip()
                break
    return body


_ACCEPTANCE_HEADING_RE = re.compile(r"^##\s+Acceptance(\s+Criteria)?\s*$", re.IGNORECASE)


def _append_criterion_box(lines: list[str], text: str) -> list[str]:
    """Add an unticked box for a declared criterion, creating the section.

    Written unticked and then rewritten by the caller, rather than written
    already-ticked: one code path composes every stamped line, so the tick and
    the reconcile forms cannot drift from the shapes REQ-BOXES parses.
    """
    out = list(lines)
    for i, line in enumerate(out):
        if not _ACCEPTANCE_HEADING_RE.match(line):
            continue
        # End of that section: the next `##`, or the end of the note.
        j = i + 1
        while j < len(out) and not re.match(r"^##\s", out[j]):
            j += 1
        while j - 1 > i and not out[j - 1].strip():
            j -= 1
        out.insert(j, f"- [ ] {text}")
        return out
    while out and not out[-1].strip():
        out.pop()
    out.extend(["", "## Acceptance Criteria", "", f"- [ ] {text}"])
    return out


def stamp_tick(
    index: Index,
    note_id: str,
    *,
    criterion: str,
    evidence: str = "",
    reason: str = "",
    actor: str = "",
    mtime: float | None = None,
) -> dict[str, Any]:
    """Resolve one criterion on a note, rewriting **that line only** (TASK-0279).

    Two forms, per DES-0005: a tick carries evidence, a reconcile carries a
    reason. Both are written from the templates above, in exactly the shape
    REQ-BOXES and PHASE-BOXES parse — a tick the validator cannot read is worse
    than no tick, because it looks resolved and does not count.

    **Located by exact criterion text, and ambiguity is a refusal.** Two
    criteria with the same prose is not a case to guess at: the mtime guard
    makes a stale match impossible to apply, and an ambiguous one would make a
    *wrong* match easy to apply.
    """
    wanted = (criterion or "").strip()
    if not wanted:
        raise WriteError("a tick needs the criterion text it resolves")
    if evidence and reason:
        raise WriteError("a criterion is ticked with evidence or reconciled with a reason, not both")
    if not evidence and not reason:
        raise WriteError("a tick needs evidence; a reconcile needs a reason")

    path = resolve_note(index, note_id)
    _check_mtime(path, mtime)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    matches = [
        i for i, line in enumerate(lines)
        if _criterion_text(line) == wanted
    ]
    if not matches:
        # **The criteria-of-record case** (TASK-0288). A requirement may declare
        # its criteria in frontmatter `acceptance:` and carry no checkboxes at
        # all — REQ-BOXES calls that "no verification record", and it is
        # precisely the state an acceptance run exists to move out of. REQ-0028
        # is in it today: four criteria, zero boxes.
        #
        # So a first tick may CREATE the box, and the guard is that the
        # criterion must appear **verbatim in that note's own `acceptance:`
        # list**. Without it this verb would become "write any line into any
        # note"; with it, the runner can only record verdicts on criteria the
        # record already declares.
        record = index.get(path)
        declared = (record.frontmatter.get("acceptance") if record else None) or []
        declared = [str(x).strip() for x in declared] if isinstance(declared, list) else []
        if wanted not in declared:
            raise WriteError(f"no criterion on {note_id} reads {wanted!r}")
        lines = _append_criterion_box(lines, wanted)
        matches = [
            i for i, line in enumerate(lines)
            if _criterion_text(line) == wanted
        ]
        if not matches:                       # pragma: no cover — defensive
            raise WriteError(f"could not record a criterion box on {note_id}")
    if len(matches) > 1:
        raise WriteError(
            f"{len(matches)} criteria on {note_id} read {wanted!r} — "
            "resolving one would be a guess about which",
        )

    idx_line = matches[0]
    original = lines[idx_line]
    leading = original[: len(original) - len(original.lstrip())]
    stamped = (
        TICK_TEMPLATE if evidence else RECONCILE_TEMPLATE
    ).format(
        text=wanted,
        evidence=evidence.strip(),
        reason=reason.strip(),
        actor=actor.strip() or "user:unknown",
        date=_today(),
    )
    # Keep the line's original indentation — a nested criterion stays nested.
    lines[idx_line] = leading + stamped

    trailing = "\n" if text.endswith("\n") else ""
    path.write_text("\n".join(lines) + trailing, encoding="utf-8")
    return {
        "id": note_id,
        "criterion": wanted,
        "form": "ticked" if evidence else "reconciled",
        "line": idx_line + 1,
        "date": _today(),
    }


def stamp_transition(
    index: Index,
    note_id: str,
    *,
    to_status: str,
    actor: str = "",
    severity: str = "",
    mtime: float | None = None,
) -> dict[str, Any]:
    """Perform one human-owned transition (TASK-0278).

    Refuses anything the table does not offer **for this note's current
    status**, so a stale renderer cannot replay an action that was legal a
    moment ago. The error names the ownership rule rather than saying
    "forbidden", because the caller is usually a person who wants to know why.
    """
    path = resolve_note(index, note_id)
    record = index.get(path)
    if record is None:
        raise WriteError(f"{note_id} is not a note this index knows", status=404)

    note_type = (record.note_type or "").strip().lower()
    current = (record.status or "").strip().lower()
    wanted = (to_status or "").strip().lower()

    # Refused here rather than only in the UI, because the UI is not the guard.
    # A design reaching this function at all means something routed around
    # `/api/design/verdict`, and the cost of letting it through is an approval
    # with no revision on it (ISS-0056).
    if note_type in VERDICT_ENDPOINTS:
        raise WriteError(
            f"a {note_type} verdict must name the revision it judged; use "
            f"{VERDICT_ENDPOINTS[note_type]} rather than a status transition "
            f"(ISS-0056)",
            status=403,
        )

    if wanted not in statuses.VOCABULARY:
        raise WriteError(
            f"{to_status!r} is not a status in this project's vocabulary",
        )

    allowed = {to for _verb, to in HUMAN_TRANSITIONS.get(note_type, {}).get(current, ())}
    if wanted not in allowed:
        offered = sorted(allowed)
        raise WriteError(
            f"a {note_type or 'note'} at {current!r} is not moved to {wanted!r} "
            f"from the cockpit"
            + (f" (offered: {offered})" if offered else "")
            + " — REQ-0026: the cockpit performs only human-owned transitions, "
            "and close-out statuses belong to the agent",
        )

    # Accept-as-severity (TASK-0284): triaging an issue *is* deciding how bad
    # it is, so the severity rides with the transition rather than needing a
    # second write. Narrow on purpose — only an issue leaving `triage`, only
    # the four documented values. Anything else is refused rather than ignored,
    # because a silently-dropped field looks exactly like one that was applied.
    sev = (severity or "").strip().lower()
    if sev:
        if note_type != "issue" or current != "triage":
            raise WriteError(
                "a severity may only be recorded while triaging an issue",
            )
        if sev not in SEVERITIES:
            raise WriteError(f"{severity!r} is not a severity this project uses")

    _check_mtime(path, mtime)
    fm_lines, body = _split_frontmatter(path.read_text(encoding="utf-8"))
    fm_lines = _set_field(fm_lines, "status", wanted)
    if sev:
        fm_lines = _set_field(fm_lines, "severity", sev)
    fm_lines = _set_field(fm_lines, "updated", _today())
    _write(path, fm_lines, body)
    return {
        "id": note_id,
        "from": current,
        "to": wanted,
        "actor": actor,
        "severity": sev or None,
        "date": _today(),
    }


DECIDE_TRANSITIONS: dict[str, tuple[str, str | None]] = {
    "adr": ("accepted", "superseded"),
    "decision": ("accepted", "superseded"),
    "requirement": ("approved", "cancelled"),
    # A design that is accepted is not yet built — `implemented` is what the
    # code shipping means, and only TASK-0219's parity check can honestly
    # claim it. Rejecting a design `cancelled` rather than `superseded`,
    # because superseded means a LATER design replaced it, which is a
    # different fact about the future.
    "design": ("accepted", "cancelled"),
}


class WriteError(Exception):
    """Refusal with a caller-facing reason. Never partially applied."""

    def __init__(self, message: str, *, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


def _today() -> str:
    return _dt.date.today().isoformat()


def resolve_note(index: Index, note_id: str) -> Path:
    """Resolve an id to a path inside the docs tree, or refuse.

    Resolution goes through the index (never string concatenation), and
    the result is re-checked against ``docs_root`` so a symlink or a
    crafted alias cannot escape (TASK-0174 precedent).
    """
    if not isinstance(note_id, str) or not note_id.strip():
        raise WriteError("missing note id")
    path = index.by_id(note_id.strip())
    if path is None:
        raise WriteError(f"unknown note: {note_id}", status=404)
    try:
        resolved = path.resolve()
        root = index.docs_root.resolve()
        resolved.relative_to(root)
    except (OSError, ValueError):
        raise WriteError("note resolves outside the docs tree", status=403) from None
    if resolved.suffix.lower() != ".md":
        raise WriteError("not a markdown note", status=400)
    return resolved


def _split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (frontmatter lines, body). Refuses a note without one —
    writing frontmatter into a note that has none would restructure it."""
    if not text.startswith("---\n"):
        raise WriteError("note has no frontmatter block", status=409)
    end = text.find("\n---", 3)
    if end == -1:
        raise WriteError("unterminated frontmatter block", status=409)
    fm_block = text[4:end]
    rest = text[end + len("\n---"):]
    if rest.startswith("\n"):
        rest = rest[1:]
    return fm_block.splitlines(), rest


#: A key introducing a block scalar (`status: >` / `|`) or an empty value
#: that opens a nested block. Replacing only the key's own line would
#: orphan the indented continuation lines beneath it and produce invalid
#: YAML — refuse instead of corrupting (independent review, 2026-07-26).
_BLOCK_OPENER_RE = re.compile(r":\s*([|>][+-]?\d*)?\s*$")


def _get_field(lines: list[str], key: str) -> str:
    """A scalar frontmatter value, or "" — enough to read a status back."""
    prefix = key + ":"
    for line in lines:
        if line.strip().startswith(prefix):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def _set_field(lines: list[str], key: str, value: str) -> list[str]:
    """Replace ``key``'s line in place, or append it.

    Only the one top-level key is touched: the `^` anchor means nested
    keys and keys quoted inside list values are left byte-identical. A
    key whose value is a block scalar or an opened nested block is
    refused rather than rewritten, because its continuation lines are
    not on the line being replaced.
    """
    pattern = re.compile(rf"^{re.escape(key)}\s*:", re.IGNORECASE)
    rendered = f'{key}: "{value}"'
    for i, line in enumerate(lines):
        if not pattern.match(line):
            continue
        follows_indented = (
            i + 1 < len(lines)
            and lines[i + 1][:1].isspace()
            and lines[i + 1].strip() != ""
        )
        if _BLOCK_OPENER_RE.search(line) and follows_indented:
            raise WriteError(
                f"{key!r} holds a multi-line value; refusing to rewrite it "
                "in place — edit the note directly",
                status=409,
            )
        lines[i] = rendered
        return lines
    lines.append(rendered)
    return lines


def _check_mtime(path: Path, expected: float | None) -> None:
    if expected is None:
        return
    try:
        actual = path.stat().st_mtime
    except OSError as exc:
        raise WriteError(f"cannot stat note: {exc}", status=500) from None
    # Filesystem mtimes are float seconds; compare with a tolerance well
    # under a human edit but above timestamp granularity.
    if abs(actual - float(expected)) > 0.01:
        raise WriteError(
            "note changed on disk since it was read — reload and retry",
            status=409,
        )


def _write(path: Path, fm_lines: list[str], body: str) -> None:
    text = "---\n" + "\n".join(fm_lines) + "\n---\n" + body
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def stamp_review(
    index: Index,
    note_id: str,
    *,
    reviewer: str,
    verdict: str,
    status: str | None = None,
    mtime: float | None = None,
) -> dict[str, Any]:
    """Write the three review fields, optionally with a status transition.

    ``verdict`` must be the desk's plan-acceptance value — the close-out
    vocabulary is refused here so a plan approval can never satisfy the
    verification gate QUALITY.md guards.
    """
    if verdict in CLOSE_OUT_VERDICTS:
        raise WriteError(
            f"{verdict!r} is the close-out review vocabulary; the desk writes "
            f"{PLAN_ACCEPTED_VERDICT!r} so plan acceptance cannot satisfy the "
            "close-out gate",
            status=400,
        )
    if verdict not in DESK_VERDICTS:
        raise WriteError(f"unsupported verdict: {verdict}", status=400)
    if not reviewer.strip():
        raise WriteError("missing reviewer")

    path = resolve_note(index, note_id)
    record = index.get(path)
    note_type = (getattr(record, "note_type", "") or "").lower()
    if note_type in GATE_BEARING_TYPES:
        raise WriteError(
            f"{note_id} is a {note_type} note — the close-out review gate reads "
            "its review_verdict, so the desk will not stamp one; review it "
            "through close-out instead",
            status=403,
        )
    _check_mtime(path, mtime)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WriteError(f"cannot read note: {exc}", status=500) from None
    fm_lines, body = _split_frontmatter(text)

    if status is not None:
        _guard_transition("review", status)
        fm_lines = _set_field(fm_lines, "status", status)
    fm_lines = _set_field(fm_lines, "reviewed_by", reviewer.strip())
    fm_lines = _set_field(fm_lines, "review_date", _today())
    fm_lines = _set_field(fm_lines, "review_verdict", verdict)
    fm_lines = _set_field(fm_lines, "updated", _today())
    _write(path, fm_lines, body)
    return {
        "id": note_id, "rel": str(path.relative_to(index.docs_root.resolve())),
        "review_verdict": verdict, "status": status,
    }


def stamp_decision(
    index: Index,
    note_id: str,
    *,
    reviewer: str,
    accept: bool,
    mtime: float | None = None,
) -> dict[str, Any]:
    """Decide a single queued note: advance it, or decline it.

    Unlike :func:`stamp_review` — which records a verdict on a *set* whose
    notes stay where they are — this performs the lifecycle move the note
    is queued for, so the transition is validated against that type's own
    vocabulary rather than a shared allow-list.

    Gate-bearing types are refused here too: a test or change reaching this
    path would mean the desk deciding something close-out owns.
    """
    path = resolve_note(index, note_id)
    record = index.get(path)
    note_type = (getattr(record, "note_type", "") or "").lower()
    if note_type in GATE_BEARING_TYPES:
        raise WriteError(
            f"{note_id} is a {note_type} note — decided at close-out, not here",
            status=403,
        )
    pair = DECIDE_TRANSITIONS.get(note_type)
    if pair is None:
        raise WriteError(
            f"{note_type or 'this'} notes are not decided from the review desk",
            status=400,
        )
    target = pair[0] if accept else pair[1]
    if target is None:
        raise WriteError(
            f"{note_type} notes have no decline transition", status=400,
        )
    normalised = target.lower()
    if normalised not in statuses.VOCABULARY:
        raise WriteError(
            f"{target!r} is not in the project-os status vocabulary", status=400,
        )
    if not reviewer.strip():
        raise WriteError("missing reviewer")

    _check_mtime(path, mtime)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WriteError(f"cannot read note: {exc}", status=500) from None
    fm_lines, body = _split_frontmatter(text)
    fm_lines = _set_field(fm_lines, "status", normalised)
    fm_lines = _set_field(fm_lines, "reviewed_by", reviewer.strip())
    fm_lines = _set_field(fm_lines, "review_date", _today())
    # ADR-0007 names the future gate predicate as "has an accepting
    # `review_verdict`", not a status check. Writing it here keeps a
    # lone-note decision legible to that gate if the advisory phase ever
    # promotes — and legible to the measurement in the meantime.
    fm_lines = _set_field(
        fm_lines, "review_verdict",
        PLAN_ACCEPTED_VERDICT if accept else PLAN_REJECTED_VERDICT,
    )
    fm_lines = _set_field(fm_lines, "updated", _today())
    _write(path, fm_lines, body)
    return {
        "id": note_id, "status": normalised, "accepted": accept,
        "review_verdict": PLAN_ACCEPTED_VERDICT if accept else PLAN_REJECTED_VERDICT,
    }


def _guard_transition(kind: str, status: str) -> None:
    normalised = (status or "").strip().lower()
    if normalised not in statuses.VOCABULARY:
        raise WriteError(
            f"{status!r} is not in the project-os status vocabulary", status=400,
        )
    allowed = ALLOWED_TRANSITIONS.get(kind, frozenset())
    if normalised not in allowed:
        raise WriteError(
            f"{status!r} is not a transition this endpoint may perform "
            f"(allowed: {sorted(allowed)})",
            status=403,
        )


def stamp_test_run(
    index: Index,
    note_id: str,
    *,
    outcome: str,
    steps: list[dict[str, Any]],
    runner: str = "",
    mtime: float | None = None,
    aborted: bool = False,
) -> dict[str, Any]:
    """Record a manual test run: status + ``last_run`` and a ``## Runs`` log.

    An aborted run writes **no status** — a half-finished run is not
    evidence either way — but its partial log is still appended, marked
    aborted, because "we started and stopped here" is worth keeping.
    """
    path = resolve_note(index, note_id)
    _check_mtime(path, mtime)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WriteError(f"cannot read note: {exc}", status=500) from None
    fm_lines, body = _split_frontmatter(text)

    today = _today()
    if not aborted:
        _guard_transition("test-run", outcome)
        fm_lines = _set_field(fm_lines, "status", outcome)
        fm_lines = _set_field(fm_lines, "last_run", today)
        if outcome == "passing":
            fm_lines = _set_field(fm_lines, "last_verified", today)
    fm_lines = _set_field(fm_lines, "updated", today)

    body = _append_run_log(
        body, today=today, outcome="aborted" if aborted else outcome,
        steps=steps, runner=runner,
    )
    _write(path, fm_lines, body)
    return {
        "id": note_id, "outcome": "aborted" if aborted else outcome,
        "last_run": None if aborted else today,
    }


_RUNS_HEADING_RE = re.compile(r"^##\s+Runs\s*$", re.IGNORECASE | re.MULTILINE)
_REVISIONS_HEADING_RE = re.compile(r"^##\s+Revisions\s*$", re.IGNORECASE | re.MULTILINE)


def _append_run_log(
    body: str, *, today: str, outcome: str,
    steps: list[dict[str, Any]], runner: str,
) -> str:
    """Append one run under ``## Runs``, creating the section if absent.

    Newest last: the section reads as a chronological log, which is how a
    "has this ever passed, and when did it start failing?" question gets
    answered by scrolling rather than by diffing git.
    """
    lines = [f"### {today} — {outcome}" + (f" (by {runner})" if runner else "")]
    for step in steps:
        result = str(step.get("result") or "").strip() or "—"
        text = str(step.get("text") or "").strip()
        entry = f"- **{result}** · {text}"
        evidence = str(step.get("evidence") or "").strip()
        if evidence:
            entry += f" — {evidence}"
        lines.append(entry)
    block = "\n".join(lines)

    match = _RUNS_HEADING_RE.search(body)
    if not match:
        return body.rstrip("\n") + "\n\n## Runs\n\n" + block + "\n"
    # Insert at the END of the Runs section — which is not the end of the
    # body unless Runs happens to be the last heading. Appending blindly
    # filed runs under whatever section followed (independent review,
    # 2026-07-26).
    rest = body[match.end():]
    next_heading = re.search(r"^##\s", rest, re.MULTILINE)
    cut = match.end() + (next_heading.start() if next_heading else len(rest))
    head, tail = body[:cut], body[cut:]
    return head.rstrip("\n") + "\n\n" + block + "\n\n" + tail.lstrip("\n")


_REVIEW_HEADING_RE = re.compile(r"^##\s+Review\s*$", re.IGNORECASE | re.MULTILINE)

#: One comment line. Parsed back out so the surface can render pins, which is
#: why the shape is fixed rather than free prose — but it stays readable as
#: Markdown, because REQ-0023's "readable without the tool" clause covers the
#: comments, not just the verdicts.
_COMMENT_RE = re.compile(
    r"^- \*\*(?P<region>[^*]+)\*\* · (?P<date>\d{4}-\d{2}-\d{2})"
    r"(?: · (?P<author>[^—]+?))? — (?P<text>.+)$",
    re.MULTILINE,
)


def append_design_comment(
    body: str, *, region: str, date: str, author: str, text: str,
) -> str:
    """Add one region-anchored comment under ``## Review``.

    The anchor is a **region id, never a coordinate**. Pixel pins die on the
    next revision, and the founding artifact went through six in one session —
    coordinate anchoring would have produced a comment set that was worthless
    by v2.

    A region of ``""`` is the document-level lane, for criticism that has no
    region: "too much violet everywhere", or a complaint about the relationship
    between two areas. Inventing a region to host those would make the region
    list a fiction.
    """
    label = region.strip() or "(document)"
    who = f" · {author.strip()}" if author.strip() else ""
    entry = f"- **{label}** · {date}{who} — {text.strip()}"
    match = _REVIEW_HEADING_RE.search(body)
    if not match:
        return body.rstrip("\n") + "\n\n## Review\n\n" + entry + "\n"
    rest = body[match.end():]
    next_heading = re.search(r"^##\s", rest, re.MULTILINE)
    cut = match.end() + (next_heading.start() if next_heading else len(rest))
    head, tail = body[:cut], body[cut:]
    return head.rstrip("\n") + "\n" + entry + "\n\n" + tail.lstrip("\n")


def read_design_comments(body: str) -> list[dict[str, str]]:
    """Parse ``## Review`` back into comments, in written order."""
    match = _REVIEW_HEADING_RE.search(body)
    if not match:
        return []
    rest = body[match.end():]
    next_heading = re.search(r"^##\s", rest, re.MULTILINE)
    section = rest[:next_heading.start()] if next_heading else rest
    out = []
    for m in _COMMENT_RE.finditer(section):
        region = m.group("region").strip()
        out.append({
            "region": "" if region == "(document)" else region,
            "date": m.group("date"),
            "author": (m.group("author") or "").strip(),
            "text": m.group("text").strip(),
        })
    return out


def stamp_design_verdict(
    index: Index,
    note_id: str,
    *,
    reviewer: str,
    verdict: str,
    revision: str,
    accept: bool | None = None,
    mtime: float | None = None,
) -> dict[str, Any]:
    """Record a design review verdict, pinned to the revision it judged.

    ``design_revision`` is the field that makes this honest. A verdict given to
    v3 says nothing about v6, and a design surface that lost that distinction
    would let an old approval launder a new design — the one way a design
    review is worse than no review at all.

    ``accept`` optionally advances the status through ``DECIDE_TRANSITIONS``:
    ``accepted`` or ``cancelled``. Note that accepting a design does **not**
    make it ``implemented`` — that is what the code shipping means, and only
    the parity check can honestly claim it.
    """
    path = resolve_note(index, note_id)
    record = index.get(path)
    note_type = (getattr(record, "note_type", "") or "").lower()
    if note_type != "design":
        raise WriteError(f"{note_id} is a {note_type or 'note'}, not a design",
                         status=409)
    _check_mtime(path, mtime)

    text = path.read_text(encoding="utf-8")
    fm_lines, body = _split_frontmatter(text)
    today = _dt.date.today().isoformat()

    fm_lines = _set_field(fm_lines, "reviewed_by", reviewer)
    fm_lines = _set_field(fm_lines, "review_date", today)
    fm_lines = _set_field(fm_lines, "review_verdict", verdict)
    fm_lines = _set_field(fm_lines, "design_revision", revision)
    fm_lines = _set_field(fm_lines, "updated", today)

    new_status = None
    if accept is not None:
        transitions = DECIDE_TRANSITIONS["design"]
        candidate = transitions[0] if accept else transitions[1]
        # Never move a design BACKWARDS (ISS-0056 round 2). `accepted` means
        # "agreed, not yet built"; `implemented` means the code shipped. A
        # design at `implemented` that is accepted at a revision would be
        # demoted to a status that is no longer true — and every design that
        # can be offered for review today is `implemented`, which is this
        # feature's own premise. The verdict is still recorded; only the
        # status move is declined, because the verdict is the honest part.
        current = str(_get_field(fm_lines, "status") or "").strip().strip('"')
        # Settled first, and for BOTH verdicts. The round-2 fix guarded only
        # `accept`, so Reject still wrote `cancelled` over `implemented` — the
        # mirror of the bug it fixed, and invisible to rank because `cancelled`
        # sits above `implemented`.
        if current in _DESIGN_SETTLED:
            new_status = None
        else:
            # Unknown status fails CLOSED — it used to be demoted silently.
            known = current in _DESIGN_KNOWN_STATUSES or not current
            new_status = candidate if known else None
        if new_status:
            fm_lines = _set_field(fm_lines, "status", new_status)

    path.write_text("---\n" + "\n".join(fm_lines) + "\n---\n" + body,
                    encoding="utf-8")
    return {"ok": True, "id": note_id, "verdict": verdict,
            "design_revision": revision, "status": new_status}


def append_revision_log(body: str, *, date: str, reason: str) -> str:
    """Record one revision under ``## Revisions`` (TASK-0220).

    Not redundant with git, for three reasons found in review:

    * **The asset diff is noise.** Two regenerated 139KB HTML files diff as a
      wall of changes, so the reasoning between revisions collapses to the
      commit subject. One line here is the only readable record.
    * **Git history is invisible to the validator**, and a squash or rebase
      destroys it silently. A log in the note is checkable.
    * REQ-0023's "readable without the tool" clause covered comments and
      verdicts but not the *process*. This closes that.

    Newest last, matching ``## Runs`` — a chronological log answers "when did
    this start looking wrong?" by scrolling rather than by bisecting.

    **No commit sha.** An entry cannot name the commit that contains it: write
    the sha, commit, and the sha is already stale; amend to correct it and the
    amend changes it again. That is self-reference, not a bug to code around.
    So the note records the *reason* and git records the *revision*, and they
    are paired by order and date — which also means the pairing survives a
    rebase that rewrites every sha.
    """
    entry = f"- {date} — {reason.strip()}"
    match = _REVISIONS_HEADING_RE.search(body)
    if not match:
        return body.rstrip("\n") + "\n\n## Revisions\n\n" + entry + "\n"
    # Insert at the end of the Revisions SECTION, not the end of the body —
    # the same bug an independent review caught in the run log on 2026-07-26.
    rest = body[match.end():]
    next_heading = re.search(r"^##\s", rest, re.MULTILINE)
    cut = match.end() + (next_heading.start() if next_heading else len(rest))
    head, tail = body[:cut], body[cut:]
    return head.rstrip("\n") + "\n" + entry + "\n\n" + tail.lstrip("\n")


CREATE_REQUEST_KEYS: frozenset[str] = frozenset(
    {"type", "title", "body", "severity", "component", "phase", "related", "actor",
     # release only (TASK-0316) — the done-but-unshipped set, computed by the
     # caller so the note carries the number the card showed.
     "features", "previous_release"}
)

#: The types the cockpit may create. Each earns its own review of what "next
#: id" and "which template" mean — FEAT-0059's Out of Scope says so, and
#: widening this silently is how a narrow door becomes a wide one.
#:
#: - ``issue`` (TASK-0280): `next_issue_id` off the index, issue template,
#:   `triage` unless a severity was supplied.
#: - ``release`` (TASK-0316): `next_release_id` off the index, release
#:   template, **always `draft`** and always with an empty `date` — the note
#:   records that a release was PREPARED, and shipping stays a person's
#:   deliberate act. Drafting writes one file and publishes nothing.
CREATABLE_TYPES: frozenset[str] = frozenset({"issue", "release"})

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def _title_slug(title: str, *, words: int = 8) -> str:
    """Filename slug in the corpus's own convention: Capitalised-Words."""
    parts = [p for p in _SLUG_RE.split(title) if p]
    return "-".join(p[:1].upper() + p[1:] for p in parts[:words]) or "Untitled"


def next_issue_id(index: Index) -> str:
    """The next ISS id, from the **index** rather than the snapshot counter.

    `sync-snapshot.py` raises `counters` to the maximum observed id at
    pre-commit (ADR-0009), so the index and the counter agree by
    construction — reading the index means a created issue does not depend on
    the snapshot being fresh, and the counter confirms the same number later.
    """
    highest = 0
    for record in index.notes_by_type("issue"):
        note_id = (record.note_id or "").strip().upper()
        if note_id.startswith("ISS-"):
            try:
                highest = max(highest, int(note_id[4:]))
            except ValueError:
                continue
    return f"ISS-{highest + 1:04d}"


def create_issue(
    index: Index,
    docs_root: Path,
    *,
    title: str,
    body: str = "",
    severity: str = "",
    component: str = "",
    phase: str = "",
    related: list[str] | None = None,
    actor: str = "",
) -> dict[str, Any]:
    """File an issue from the template (TASK-0280).

    `status: triage` unless a severity was supplied — capture is deliberately
    dumber than intake (FEAT-0061): a title now beats a paragraph never, and
    an agent can be dispatched at the triage row when investigation is worth
    it. Supplying a severity means the judgment has already been made, so the
    issue opens rather than queueing for one.
    """
    clean_title = (title or "").strip()
    if not clean_title:
        raise WriteError("an issue needs a title")

    sev = (severity or "").strip().lower()
    if sev and sev not in {"critical", "high", "medium", "low"}:
        raise WriteError(f"{severity!r} is not a severity this project uses")

    issue_id = next_issue_id(index)
    target = docs_root / "issues" / f"{issue_id}-{_title_slug(clean_title)}.md"
    # Path canonicalisation, as everywhere else in this module: the computed
    # target must land inside docs_root, whatever the title contained.
    resolved = target.resolve()
    if not str(resolved).startswith(str(docs_root.resolve())):
        raise WriteError("refusing to write outside the docs root")
    # Collide on the **id**, not the filename. Two creates against the same
    # stale index compute the same id from different titles, so a filename
    # check passes and two notes end up sharing an id — which the validator
    # would report much later, on someone else's afternoon.
    existing = sorted(resolved.parent.glob(f"{issue_id}-*.md")) if resolved.parent.is_dir() else []
    if existing or resolved.exists():
        raise WriteError(
            f"{issue_id} already exists at {existing[0].name if existing else resolved.name} "
            "— the index is stale; rebuild it and retry",
            status=409,
        )

    today = _today()
    lines = [
        "---",
        'type: "[[issue]]"',
        f"id: {issue_id}",
        f'aliases: ["{issue_id}"]',
        f'title: "{clean_title.replace(chr(34), chr(39))}"',
        f"status: {'open' if sev else 'triage'}",
        f'phase: "{phase}"' if phase else 'phase: ""',
        f"owner: {actor.strip() or 'unassigned'}",
        f"created: {today}",
        f"updated: {today}",
        f'source: ["captured in the cockpit, {today}"]',
        f"severity: {sev or 'medium'}",
        f'component: "{component.strip()}"',
        'parent: ""',
        "related: [" + ", ".join(f'"{r}"' for r in (related or [])) + "]",
        "tests: []",
        "---",
        "",
        f"# {clean_title}",
        "",
        "## Problem",
        "",
        (body or "").strip() or "<captured without a description>",
        "",
    ]
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text("\n".join(lines), encoding="utf-8")
    return {
        "id": issue_id,
        "rel": str(resolved.relative_to(docs_root.resolve())),
        "status": "open" if sev else "triage",
        "severity": sev or "medium",
    }


def draft_issue_body(
    test_id: str, test_title: str, step: dict[str, Any],
) -> dict[str, str]:
    """Shape a failing step into an issue-intake draft (TASK-0209).

    Returned as data for the user to confirm — the cockpit never files an
    ISS on its own, because allocating an id is a documentation decision
    and LIFECYCLE puts that in preflight, not in a UI callback.

    Wired into ``POST /api/notes/test-run``'s **response** by TASK-0372 — not
    into ``stamp_test_run``, which is the write path and did not move. Until
    then this had no caller outside its own unit test, while two records said
    it did.
    """
    expected = str(step.get("expected") or "").strip() or "(not recorded in the test)"
    observed = str(step.get("evidence") or "").strip() or "(not recorded)"
    title = f"{test_title or test_id} — step {step.get('n')} failed"
    body = (
        f"Found while running [[{test_id}]] manually from the Tests view.\n\n"
        f"**Step {step.get('n')}:** {str(step.get('text') or '').strip()}\n\n"
        f"**Expected:** {expected}\n\n"
        f"**Observed:** {observed}\n"
    )
    return {"title": title, "body": body, "test_id": test_id}


def next_release_id(index: Index) -> str:
    """The next REL id, from the index — same rule as :func:`next_issue_id`.

    `counters.REL` read `0` for six months across 85 features, so this is the
    first allocation path that has ever incremented it.
    """
    highest = 0
    for record in index.notes_by_type("release"):
        note_id = (record.note_id or "").strip().upper()
        if note_id.startswith("REL-"):
            try:
                highest = max(highest, int(note_id[4:]))
            except ValueError:
                continue
    return f"REL-{highest + 1:04d}"


def create_release(
    index: Index,
    docs_root: Path,
    *,
    title: str,
    features: list[str] | None = None,
    previous_release: str = "",
    actor: str = "",
) -> dict[str, Any]:
    """Scaffold a release note from the template, as a **draft** (TASK-0316).

    `status: draft` is not a placeholder — `STATUSES.md` defines it as
    *"prepared and verified, not yet live"*, and the actuator row is what
    advances it to `released`. **Drafting publishes nothing**: it allocates an
    id and writes one file under `docs/releases/`. No push, no deploy, no
    remote — FEAT-0055's line, that a commit is local and reversible while
    publishing is a person's deliberate act, applies with more force here.

    `features:` arrives already computed (the done-but-unshipped set) rather
    than being derived here, so the number the card showed is the number the
    note carries. Deriving it a second time is how the two would disagree.

    `date:` is deliberately left empty. It records when the release *shipped*,
    and a drafted note has not.
    """
    clean_title = (title or "").strip()
    if not clean_title:
        raise WriteError("a release needs a title")

    release_id = next_release_id(index)
    target = docs_root / "releases" / f"{release_id}-{_title_slug(clean_title)}.md"
    resolved = target.resolve()
    if not str(resolved).startswith(str(docs_root.resolve())):
        raise WriteError("refusing to write outside the docs root")
    # Collide on the id, not the filename — `create_issue`'s reasoning, which
    # is about two creates racing a stale index rather than about issues.
    existing = sorted(resolved.parent.glob(f"{release_id}-*.md")) if resolved.parent.is_dir() else []
    if existing or resolved.exists():
        raise WriteError(
            f"{release_id} already exists at {existing[0].name if existing else resolved.name} "
            "— the index is stale; rebuild it and retry",
            status=409,
        )

    today = _today()
    feature_links = ", ".join(f'"[[{f}]]"' for f in (features or []))
    lines = [
        "---",
        'type: "[[release]]"',
        f"id: {release_id}",
        f'aliases: ["{release_id}"]',
        f'title: "{clean_title.replace(chr(34), chr(39))}"',
        "status: draft",
        'version: ""',
        'tag: ""',
        # Empty on purpose: `date` is when it shipped, and this has not.
        'date: ""',
        "platform:",
        f"owner: {actor.strip() or 'unassigned'}",
        f"created: {today}",
        f"updated: {today}",
        f"features: [{feature_links}]",
        "changes: []",
        "tests_verified: []",
        f'previous_release: "{previous_release}"',
        "related: []",
        "tags: [release]",
        "---",
        "",
        f"# {clean_title}",
        "",
        "## Scope",
        "",
        f"Scaffolded in the cockpit on {today} from the done-but-unshipped set — "
        f"{len(features or [])} feature(s). Drafting allocated an id and wrote this "
        "file; it published nothing.",
        "",
        "## Verification",
        "",
        "The Tier 1/2 gate blocks a release while any check is unticked "
        "(`tools/instructions/TESTING.md`). Record exceptions here, with "
        "justification, or walk the checks.",
        "",
        "## Notes",
        "",
        "<what this release is, and what it does not claim>",
        "",
    ]
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text("\n".join(lines), encoding="utf-8")
    return {
        "id": release_id,
        "rel": str(resolved.relative_to(docs_root.resolve())),
        "status": "draft",
        "features": list(features or []),
    }


_ACCEPTANCE_RUNS_RE = re.compile(r"^##\s+Acceptance runs\s*$", re.IGNORECASE | re.MULTILINE)

#: What a completed run may leave on the feature. `accepted_by` is written by
#: **this path only** (REQ-0028): "no path stamps it directly".
ACCEPTANCE_RUN_KEYS: frozenset[str] = frozenset(
    {"id", "passed", "failed", "skipped", "issues", "actor", "mtime", "complete"}
)


def stamp_acceptance_run(
    index: Index,
    feature_id: str,
    *,
    passed: int,
    failed: int,
    skipped: int,
    issues: list[str] | None = None,
    complete: bool = True,
    actor: str = "",
    mtime: float | None = None,
) -> dict[str, Any]:
    """Record an acceptance run on a feature (TASK-0289).

    Appends under ``## Acceptance runs`` in `_append_run_log`'s grammar, and —
    **only when the run completed** — stamps `accepted_by` / `accepted_date`.

    REQ-0028's four criteria, each load-bearing:

    * *"Every tick the runner writes carries who and when, machine-composed —
      never typed, never omitted"* — the witness comes from `actor`, which the
      server takes from the request, and the date from `_today()`. Neither is
      free text on this path.
    * *"A run's log line names the same witness and totals"* — one composed
      line, so the log and the frontmatter cannot disagree.
    * *"accepted_by is only ever written by a completed run"* — an incomplete
      run appends its log and stamps nothing. A partial walk is evidence of
      progress, not of acceptance.
    * *"An agent cannot be a witness"* — enforced at the route by
      `_require_loopback` plus REQ-0026's ownership terms, not here; this
      records whoever the guarded caller says it is.

    A feature that never requested acceptance is refused: stamping
    `accepted_by` on a feature nobody asked about would manufacture a judgment.
    """
    path = resolve_note(index, feature_id)
    record = index.get(path)
    note_type = (record.note_type if record else "") or ""
    if note_type != "feature":
        raise WriteError(
            f"{feature_id} is a {note_type or 'note'}; acceptance runs are recorded "
            "on features"
        )
    _check_mtime(path, mtime)

    text = path.read_text(encoding="utf-8")
    fm_lines, body = _split_frontmatter(text)
    requested = _get_field(fm_lines, "acceptance").strip().strip('"').lower()
    # **The run is always recorded; only the STAMP is conditional** (DES-0006).
    # The feature-note entry point exists "for accepting anything on demand,
    # opted-in or not", so refusing the whole call would make a walk impossible
    # on any feature that had not opted in — which is most of them. What must
    # not happen is `accepted_by` appearing on a feature nobody asked about,
    # because that manufactures a judgment.
    #
    # An earlier cut refused the call outright and was caught walking a real
    # run against FEAT-0063, which carries no `acceptance:` field at all.
    stamps = complete and requested == "requested"

    witness = (actor or "").strip() or "unassigned"
    today = _today()
    filed = ", ".join(issues or [])
    outcome = (
        f"{passed} passed · {failed} failed"
        + (f" → {filed}" if filed else "")
        + f" · {skipped} skipped"
    )
    if not complete:
        outcome += " · INCOMPLETE"
    elif not stamps:
        outcome += " · not accepted (acceptance was not requested)"

    heading_match = _ACCEPTANCE_RUNS_RE.search(body)
    block = f"### {today} — {witness} — {outcome}"
    if not heading_match:
        body = body.rstrip("\n") + "\n\n## Acceptance runs\n\n" + block + "\n"
    else:
        rest = body[heading_match.end():]
        nxt = re.search(r"^##\s", rest, re.MULTILINE)
        cut = heading_match.end() + (nxt.start() if nxt else len(rest))
        head, tail = body[:cut], body[cut:]
        body = head.rstrip("\n") + "\n\n" + block + "\n\n" + tail.lstrip("\n")

    if stamps:
        fm_lines = _set_field(fm_lines, "accepted_by", witness)
        fm_lines = _set_field(fm_lines, "accepted_date", today)
        fm_lines = _set_field(fm_lines, "acceptance", "accepted")
    fm_lines = _set_field(fm_lines, "updated", today)
    _write(path, fm_lines, body)
    return {
        "id": feature_id,
        "rel": record.rel_path if record else "",
        "witness": witness,
        "date": today,
        "complete": complete,
        "accepted": stamps,
        # Said out loud so the surface can report it: a completed walk on a
        # feature that never opted in is a recorded run and NOT an acceptance,
        # and silence about that difference is how one would read as the other.
        "requested": requested or "",
        "outcome": outcome,
    }


#: What an attach request may carry.
ATTACH_REQUEST_KEYS: frozenset[str] = frozenset(
    {"id", "png_base64", "caption", "actor", "inbox_name"}
)

#: Where evidence lands. Under `docs/` **on purpose**: `inbox/` is gitignored
#: staging for material nobody has decided about, and a screenshot that proves
#: a criterion is the opposite of that — it is the record (FEAT-0066).
ATTACHMENTS_DIR = "attachments"

#: A conservative ceiling. A window capture is a few hundred KB; anything past
#: this is either not a screenshot or not something to put in git history,
#: where it cannot be removed by deleting the file later.
MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024


def attach_capture(
    index: Index,
    docs_root: Path,
    note_id: str,
    *,
    png_base64: str,
    caption: str = "",
    actor: str = "",
) -> dict[str, Any]:
    """Store a capture as evidence against a note (TASK-0297).

    Lands at ``docs/attachments/<NOTE-ID>/<date>-<n>.png`` and returns the
    Markdown that cites it, ready to paste into a criterion's evidence or a
    run log. The `/docs/<path>` route already serves anything under `docs/`
    and the renderer already rewrites image sources, so the picture renders
    with no new read path — which is why this lands here rather than beside
    the design artifacts.

    **Committed, deliberately.** Evidence that lives only on one machine is
    the chat-transcript problem [[REQ-0028]] exists to prevent, one layer
    down: a witness with no artifact.

    The note must exist. Writing evidence for an id nobody allocated would
    create a directory the record cannot explain.
    """
    import base64
    import binascii

    resolve_note(index, note_id)              # raises if the note is unknown
    raw = (png_base64 or "").strip()
    if raw.startswith("data:"):
        raw = raw.split(",", 1)[-1]
    if not raw:
        raise WriteError("an attachment needs image data")
    try:
        blob = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise WriteError(f"attachment is not valid base64: {exc}") from None
    if len(blob) > MAX_ATTACHMENT_BYTES:
        raise WriteError(
            f"attachment is {len(blob)} bytes; the ceiling is "
            f"{MAX_ATTACHMENT_BYTES} — git history cannot forget a large blob",
            status=413,
        )
    # A PNG and nothing else: the renderer will emit an <img> for whatever is
    # here, and serving an arbitrary uploaded byte stream from the docs tree
    # is a different feature with a different threat model.
    if not blob.startswith(b"\x89PNG\r\n\x1a\n"):
        raise WriteError("attachment is not a PNG")

    safe_id = re.sub(r"[^A-Za-z0-9-]", "", note_id.upper())
    if not safe_id:
        raise WriteError(f"{note_id!r} is not an id an attachment can be filed under")
    target_dir = (docs_root / ATTACHMENTS_DIR / safe_id).resolve()
    if not str(target_dir).startswith(str(docs_root.resolve())):
        raise WriteError("refusing to write outside the docs root")
    target_dir.mkdir(parents=True, exist_ok=True)

    today = _today()
    n = 1
    while (target_dir / f"{today}-{n}.png").exists():
        n += 1
    target = target_dir / f"{today}-{n}.png"
    target.write_bytes(blob)

    rel = target.relative_to(docs_root.resolve()).as_posix()
    alt = (caption or "").strip() or f"{note_id} evidence {today}"
    return {
        "id": note_id,
        "rel": rel,
        "url": f"/docs/{rel}",
        "markdown": f"![{alt}](/docs/{rel})",
        "bytes": len(blob),
        "actor": (actor or "").strip(),
    }


CHOOSE_VARIANT_KEYS: frozenset[str] = frozenset({"id", "variant", "actor", "mtime"})


def stamp_chosen_variant(
    index: Index,
    note_id: str,
    *,
    variant: str,
    actor: str = "",
    mtime: float | None = None,
) -> dict[str, Any]:
    """Record which variant a design chose (TASK-0302).

    Writes `chosen_variant` and nothing else — **it does not accept the
    design**. Choosing a shape and accepting a design are two judgments, and
    collapsing them would let a click on a thumbnail carry an acceptance
    nobody made. Acceptance still goes through `stamp_design_verdict`, pinned
    to the revision it judged (ISS-0056's rule).

    The variant must exist in the note. A `chosen_variant` naming a section
    that was never written is a record of a decision about nothing.
    """
    from .cockpit import design_variants

    wanted = (variant or "").strip()
    if not wanted:
        raise WriteError("a choice needs the variant's name")
    path = resolve_note(index, note_id)
    record = index.get(path)
    if (record.note_type if record else "") != "design":
        raise WriteError(f"{note_id} is not a design; variants live on designs")
    _check_mtime(path, mtime)

    text = path.read_text(encoding="utf-8")
    names = [v["name"] for v in design_variants(text)]
    if wanted not in names:
        raise WriteError(
            f"{note_id} has no variant named {wanted!r} "
            f"(it has: {', '.join(names) or 'none'})"
        )

    fm_lines, body = _split_frontmatter(text)
    fm_lines = _set_field(fm_lines, "chosen_variant", wanted)
    fm_lines = _set_field(fm_lines, "updated", _today())
    _write(path, fm_lines, body)
    return {
        "id": note_id,
        "chosen_variant": wanted,
        "variants": names,
        "actor": (actor or "").strip(),
        # Said explicitly so a caller cannot read silence as acceptance.
        "accepted": False,
    }
