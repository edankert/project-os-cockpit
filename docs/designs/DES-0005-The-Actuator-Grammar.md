---
type: "[[design]]"
id: DES-0005
aliases: ["DES-0005"]
title: "The actuator grammar — how a human action appears on a note, which actions exist, and why the server decides"
role: proposal
status: draft
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Review 2026-08-03: 'the human has no levers' — every transition in STATUSES.md's table is agent-owned, and the cockpit's only actuator is asking an agent in the terminal"]
asset: ""
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[FEAT-0059-The-Write-Service-Widens]]", "[[FEAT-0060-Transitions-And-Ticks-On-The-Note]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[DES-0002-Cockpit-Design-System]]"]
---

# The actuator grammar

## The principle, inherited not invented

`note_writes.py` already crossed the viewer line once, for ADR-0007, and wrote down the terms: *the cockpit writes only to record a decision a human made in the UI*. Every allow-list, precondition and refusal in this design is that sentence applied again. The module already has the shapes — `DECIDE_TRANSITIONS` (adr → accepted, requirement → approved/cancelled, design → accepted/cancelled), mtime preconditions, loopback checks, atomic writes. This design extends its tables; it does not invent a second writer.

## What the human can do, by type

Drawn from STATUSES.md's vocabulary, taking only judgments that are inherently the asker's:

| type | state | actions offered |
|---|---|---|
| requirement | `draft`/`proposed` | **Approve** · Decline |
| adr / decision | `proposed` | **Accept** · Supersede… |
| design | `proposed` | **Accept** (stamps `design_revision`) · Decline |
| issue | `triage` | **Accept as** severity picker · Decline |
| feature | any, `acceptance:` requested | **Start acceptance run** (PHASE-024) |
| any with criteria | criterion unticked | **Tick…** (evidence prompt) · Reconcile… (`[~]` + reason) |
| question (queue) | open | **Answer…** (writes to the asking session) |
| changes-requested (register) | — | **Request re-review** (dispatch) |

Deliberately absent: every agent-owned transition — close-out statuses (`done`, `fixed`, `merged`, `implemented`), anything test-gated, anything the validator computes. The endpoint refuses them; the renderer never shows them. Two independent layers, because ISS-0023 taught what happens when the renderer's list is the only list.

## The server decides, the renderer displays

`GET /api/notes/actions?id=` returns the legal actions for a note's current state. The renderer draws buttons from the payload and sends the chosen action back with the note's `mtime`. **No vocabulary in TypeScript** — the ownership table lives in one Python module beside the transitions it guards, and the parity suite checks nothing because there is nothing to drift.

Failure modes are first-class: an action can arrive `disabled` with a `reason` ("2 criteria unresolved", "note changed since render — reload"), because a button that vanishes teaches nothing while a button that explains does.

## Where actions live on the note

A single quiet row under the note's title in the centre pane — the record grammar's metrics (11px caps for the row label, buttons at chip height). Not in the panes: the left pane is a selection list and the right a description; an actuator belongs on the thing being actuated. One confirmation step for terminal moves (Decline, Supersede), none for forward moves — reversing an approve is itself a recorded action, so the cost of a slip is an extra line of history, not lost work.

Ticking: rendered `- [ ]` checkboxes in criteria sections become live. Click → inline evidence field ("what shows this is met?") → writes `- [x] … — evidence: <text> (user:edwin, 2026-08-03)` in exactly the shape REQ-BOXES/PHASE-BOXES validate. Reconcile writes the `- [~]` form with its reason. The write is a body edit scoped to one line, located by criterion text match with the mtime guard making a stale match impossible to apply.

## The write path

One new endpoint per verb, all POST, all through the existing guards:

- `/api/notes/transition` — id, action, mtime → `DECIDE_TRANSITIONS`-style table extended per the matrix above
- `/api/notes/tick` — id, criterion text, evidence|reconcile-reason, mtime
- `/api/notes/create` — type=issue only for now (FEAT-0061): template + next free ID from the index (the counter stays sync-snapshot's; the index's max+1 is the same number sooner)

All loopback-only by the existing `_require_loopback`. The 0.0.0.0 render surface stays read-only — [[RISK-0005]] is the standing record of why that must never relax.

## Rejected alternatives

- **Editing frontmatter in a form.** Generic editing is authorship, not judgment; it belongs to whoever writes the note. The narrow verbs are the design.
- **The renderer holding the transition table.** Third restatement of a vocabulary that drifted twice this week under exactly that arrangement.
- **Auto-confirm dialogs everywhere.** One confirmation for terminal moves only; friction spent where mistakes cost.
