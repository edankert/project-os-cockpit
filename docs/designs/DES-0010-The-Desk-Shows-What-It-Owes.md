---
type: "[[design]]"
id: DES-0010
aliases: ["DES-0010"]
title: "The desk shows what it owes — the board as the centre pane's empty state, the registers as the record, and the walk unchanged"
role: proposal
status: "proposed"
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-09
source: ["Session 2026-08-09: Edwin proposed a kanban view for the overview; the status axis was measured empty (1 in-flight work item here, 77 fleet-wide) and the request was redirected to ~review, whose obligation axis is the one with occupancy"]
asset: "DES-0010-desk-shows-what-it-owes.html"
implements: []
supersedes: ""
superseded_by: ""
reviewed_by: ""
review_date: ""
review_verdict: ""
related: ["[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[DES-0005-The-Actuator-Grammar]]", "[[DES-0006-The-Acceptance-Desk]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[REQ-0026-Only-Human-Owned-Transitions]]", "[[DES-0002-Cockpit-Design-System]]"]
tags: [design, review-desk]
---

# The desk shows what it owes

## Problem

Two problems, and the second is the reason the first is worth fixing.

**The desk overstates what it owes by a factor of four.** `Changes requested · 10` is the most prominent thing on it, and all ten subjects are terminal ([[ISS-0121]]). Its real load is three `draft` requirements.

**The desk's panes are inverted.** Measured against this corpus:

| pane | width | contents |
|---|---|---|
| left | 240 px | `Queue · 3` → Proposals 3 → Changes requested 10 → `Tests · 23/23` → `Completed · 4` (93 items) — **39 rows**, 3 of them real |
| centre | ~576 px | one sentence: *"Pick something from the queue"* |
| right | 280 px | cleared on entry (`renderer.ts:4105`) |

Everything owed is in the narrowest pane, outnumbered nine to one by registers that are not owed at all; the widest pane holds eight words; the third is blank. A reader cannot see the *shape* of what is owed without reading a scrolling list, and at the fleet's busiest desk — `your-trainer`, 39 owed — the list is all there is.

## Approach

**The centre pane's empty state becomes the board.** Not a new surface: `buildReviewEmpty()` is replaced, and clicking a card swaps in the detail view exactly as today. [[DES-0006]] rejected "a separate acceptance app/page" because a second desk splits the queue; this keeps one desk and gives its idle state a job.

**Columns are obligation kinds, and they ship in the payload.** Today's four groups merge things whose verb differs — a `draft` requirement is *approved*, an offered design revision is *accepted*. [[DES-0005]]'s table already draws that distinction; the payload should carry a `verb` beside each group so no vocabulary lives in TypeScript. That is the [[ISS-0023]] rule applied before it can be broken rather than after.

**Occupied columns take the width; empty kinds collapse to one line.** This is the load-bearing decision. Five of six kinds are empty here, and drawing six columns would reproduce exactly the failure that made a status kanban the wrong answer in the first place — a board whose information is its middle column, rendered mostly empty. One line of `nothing to decide · nothing to accept · nothing to answer` keeps the completeness at a twentieth of the cost.

**The board and the queue-list are one payload in two modes, never both on screen.** Nothing selected → centre shows the board, left pane shows the registers. Something selected → centre shows the detail, left pane becomes the queue with the current row lit and a `1 of 3` / `Next ▸` walk. At three items a board *and* a list would be visibly redundant; at thirty-nine the board is the map and the list is the walk. Switching by mode gets both without keeping two lists in sync.

**No write path is added.** The board navigates. Every actuator in plate C is [[DES-0005]]'s, on the note being actuated, behind [[REQ-0026]]: the cockpit performs only human-owned transitions, and `done` / `fixed` / `merged` are the agent's.

## Why not the status kanban that was asked for

Recorded because it is the obvious request and the measurement is what refuted it, not taste.

The information in a kanban is the distribution across its columns, and the column that carries it is the middle one. This corpus has **1** in-flight work item (353 tasks: 282 `done`, 65 `backlog`, 0 `doing`); the fleet has 77 across 4,630 notes, and six of twelve repos have two or fewer. A three-column board renders `65 | 1 | 282`. [[DES-0001]]'s states audit had already found the cause — work here is bursty, `doing` and `triage` clear within a session — which is why the overview is designed quiet-first.

Dragging a card between columns is also refused server-side whatever a renderer draws, so the half of a kanban that makes it a tool rather than a layout is unavailable by contract.

The obligation axis is the one with occupancy, and — unlike status — it is durable: 3 here, 39 in `your-trainer`, 23 in `your-health`, all of them states that persist across sessions because they are waiting on a person.

## Regions

Six top-level, one per plate, plus the two reference sections. Granularity matches what a reviewer comments at — a plate, or the table beneath it.

- `plate-a` — the desk as built, with the pane inversion pinned
- `plate-b` — proposed, arriving: board in the centre, registers left
- `plate-c` — proposed, inside an item: detail, actuator row, the walk
- `plate-d` — the same board at `your-trainer`'s 39 owed
- `plate-e` — card anatomy against the 240 px row it replaces
- `columns` — every column, its source, its count here and in `your-trainer`, and what must change
- `cost` — what each piece costs and what it must not break
- `notes` — the document-level lane for criticism that belongs to no single plate

## Tokens

The artifact declares `--status-*`, `--severity-*` and `--type-*` **verbatim from the implementation**, both schemes, in the implementation's own order: `:root` carries the light values from `base.css` / `cockpit.css`, `[data-theme="dark"]` the dark ones. `design_tokens.py` compares first-declaration-wins, so a dark-only plate declaring dark values under `:root` would report a divergence that does not exist — the trap that module's docstring describes. Declaring both blocks means the parity check compares light against light and passes for the right reason.

The artifact renders dark by default (`<html data-theme="dark">`) with a toggle, so both schemes can be reviewed. No token is re-typed as hex; every value is the `hsl(...)` triple the stylesheet holds.

Layout values are the shell's own: `44px` rail, `240px` nav, `1fr` centre, `280px` right (`renderer.css:61`).

## Out of scope

- **Any write path.** No transition, tick, or creation. Those are [[FEAT-0059]]'s, and this design consumes them at most by displaying what the server already offers.
- **The acceptance column.** [[DES-0006]]'s `Awaiting your acceptance · N` belongs on this board and is drawn in the columns table as a seventh row, but it is unbuilt and this design does not build it.
- **Fixing [[ISS-0121]].** Named as a prerequisite, specified there, not here. The layout must not land first: it would render ten false obligations more prominently than the current list does.
- **The overview.** The surface the request started from is unchanged. `~review` is where obligations live.
- **A fleet board.** Considered and dropped at Edwin's direction — he works one repo at a time, so a cross-repo board would serve a use that does not occur.

## Revisions

- 2026-08-09 — first revision. Five plates drawn from live payloads (this repo and `your-trainer`), not from sketches.

## Review

<Region-anchored comments land here. Verdicts go in the frontmatter, transcribed from a review that actually happened — never anticipated.>
