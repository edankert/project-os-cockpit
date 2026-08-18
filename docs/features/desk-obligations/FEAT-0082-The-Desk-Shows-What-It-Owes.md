---
type: "[[feature]]"
id: FEAT-0082
aliases: ["FEAT-0082"]
title: "The desk shows what it owes — the board as the centre pane's landing, the registers as the record, and the walk made explicit"
status: superseded
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-09
updated: 2026-08-10
source: ["[[DES-0010-The-Desk-Shows-What-It-Owes]]"]
goal: "Give ~review's centre pane a job when nothing is selected — the shape of what is owed, by obligation kind, from the payload the desk already serves — and stop the 240px pane carrying 39 rows of which 3 are actionable."
requirements: ["[[REQ-0026-Only-Human-Owned-Transitions]]"]
tasks:
  - "[[TASK-0357-Obligation-Groups-And-Verbs-In-The-Payload]]"
  - "[[TASK-0358-The-Board-Is-The-Desks-Landing]]"
  - "[[TASK-0359-The-Pane-Is-The-Walk]]"
  - "[[TASK-0360-The-Right-Pane-Carries-The-Note]]"
design: "[[DES-0010-The-Desk-Shows-What-It-Owes]]"
superseded_by: "[[ADR-0020-Obligations-Live-With-Their-Subject]]"
release: ""
related: ["[[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]", "[[DES-0005-The-Actuator-Grammar]]", "[[FEAT-0049-Review-Desk-As-Record]]", "[[FEAT-0041-Review-Desk]]", "[[TST-0022-Surface-Ownership]]"]

---

# The desk shows what it owes

## Goal

`~review` puts everything owed in its narrowest pane and one sentence in its widest. Measured on this corpus: **39 rows** in the 240 px pane, 3 of them actionable, against *"Pick something from the queue"* in ~576 px and a right pane cleared on entry. At `your-trainer`'s 39 owed the list is all there is, with no shape to read.

The board makes the shape legible without adding a surface: it replaces the centre pane's empty state, and clicking a card opens the detail view that already exists.

## Scope

**In:**

- Obligation groups in `review_queue_payload`, each carrying its verb — `Proposals` splits into **Approve** (requirement `draft`) and **Accept** (design `proposed` + ledger offers), because those are different judgments and [[DES-0005]]'s table already says so.
- A board as the desk's landing: occupied columns at width, empty kinds on one line, cards carrying full title / type / state / owning phase / age.
- The left pane by mode — registers when nothing is selected, the queue with `1 of N` and `Next ▸` when something is.
- The right pane carrying the selected note's context instead of being blanked.

**Out:**

- **Any write path.** The board navigates. Actuators are [[FEAT-0060]]'s, on the note, behind [[REQ-0026]]. Nothing here can reach `done` / `fixed` / `merged`.
- **[[ISS-0121]]**, which is a prerequisite and not part of this feature. Building the board first would render ten false obligations more prominently than the current list does.
- **[[DES-0006]]'s acceptance column.** It belongs on this board and is drawn in the design's column table; it is built when the acceptance runner is.
- **The overview.** The surface the request started from is unchanged.

## Why this sits in PHASE-023

The phase's goal is that the human's judgments become actions in the cockpit. [[FEAT-0062]] (desk resolution flows) already lives here, and the actuator row in [[DES-0010]]'s plate C *is* [[DES-0005]]'s. This feature is the surface those levers land on: it makes what is owed visible, they make it actionable. Opening a phase for one display feature is what [[ISS-0077]] forbade.

## Acceptance

- [ ] With nothing selected, `~review`'s centre pane shows one column per occupied obligation kind, and the kinds with nothing owed appear as a single line rather than as empty columns
- [ ] Column labels and verbs come from the payload; no obligation vocabulary is declared in TypeScript (guarded in the [[ISS-0023]] style — removing a group server-side removes its column with no renderer change)
- [ ] A card carries the full title, type, state, owning phase and age — every field the 240 px row puts in a `title` tooltip
- [ ] Selecting a card opens the existing detail view unchanged, and the left pane becomes the queue with the current row marked and a working `Next ▸`
- [ ] The board and the queue list are never both on screen
- [ ] The right pane shows the selected note's context and is no longer cleared on entry
- [ ] No new write endpoint, and no status the server would refuse appears on any card or control
- [ ] [[TST-0022]]'s pane-order step is updated to describe the mode-dependent pane, and passes

## Links

- Design: [[DES-0010-The-Desk-Shows-What-It-Owes]] — five plates, drawn from live payloads
- Prerequisite: [[ISS-0121-Reviewed-Register-Counts-Settled-Work-As-Owed]]
- Requirements: [[REQ-0026-Only-Human-Owned-Transitions]]
- Paths: `src/project_os_cockpit/cockpit.py` (`review_queue_payload`, `_reviewed_register`), `desktop/src/renderer/renderer.ts` (`buildReviewEmpty`, `renderReviewQueuePane`, `renderReviewPage`), `desktop/src/renderer/renderer.css`


## Superseded 2026-08-10 — [[ADR-0020]]

The board this builds lives on `~review`, which [[ADR-0020]] retires. [[PHASE-030]] does the same job differently: obligations surface in the view owning their subject, and the count moves to the view buttons.

Its four tasks are superseded with it, and one is explicitly carried forward — [[TASK-0357]]'s server-owned obligation vocabulary is now [[FEAT-0089]]'s registry, applied to every kind rather than to the desk's four groups. [[TASK-0360]]'s point (the note's context should be on screen while it is judged) survives as a property of judging on the note rather than in a queue.

[[ISS-0121]], filed while designing this, is unaffected and moved to [[PHASE-030]].
