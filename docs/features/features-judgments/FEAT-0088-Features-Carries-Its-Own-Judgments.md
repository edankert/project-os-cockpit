---
type: "[[feature]]"
id: FEAT-0088
aliases: ["FEAT-0088"]
title: "Features carries its own judgments — requirement approval and acceptance surface beside the work they concern"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "Edwin 2026-08-10: 'if we need any human decisions/refinement for any of these items then it makes sense to show them here'"]
goal: "Surface the two judgments the work tree asks for — approve a draft requirement, accept a finished feature — on the feature they belong to, so approving is done with the thing being specified in view."
requirements: []
tasks:
  - "[[TASK-0376-Approval-And-Acceptance-On-The-Feature]]"
release: ""
related: ["[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0085-The-Navigator-Shows-The-Structure-The-Record-Has]]", "[[DES-0006-The-Acceptance-Desk]]", "[[FEAT-0063-The-Acceptance-Runner]]", "[[FEAT-0064-The-Acceptance-Gate]]"]

---

# Features carries its own judgments

## Goal

Two obligations belong to the work tree, and both sat on a queue that showed them without their subject:

- **A `draft` requirement awaits approval.** It is already nested under the feature it specifies. Approving it from a queue row meant judging "should this constrain the work" without the work on screen.
- **A feature carrying `acceptance: requested` awaits an acceptance run.** [[DES-0006]] made this its first entry point — *"the desk queue gains `Awaiting your acceptance · N`"* — and [[ADR-0020]] moves that entry point here.

## Scope

**In:** requirement `draft` → **approve** and feature `acceptance: requested` → **accept**, as this view's obligations from [[FEAT-0089]]'s registry, with the badge; the entry point to the acceptance run; `changes-requested` on a feature or task surfacing in the tree.

**Out:**

- **The acceptance runner itself.** [[FEAT-0063]]/[[FEAT-0064]] under [[PHASE-024]] own the criterion-by-criterion walk, the witness evidence and the `acceptance:` gate. This gives them their entry point, nothing more.
- The actuators. [[DES-0005]]'s row on the note performs the transition; this feature makes the obligation visible and reachable.
- The tree's shape — [[FEAT-0085]] owns tasks joining the tree, and lands independently.

## Interaction with FEAT-0085

Both change the Features view and can land in either order, but they touch the same payload. [[FEAT-0085]] adds task children; this adds obligation marks and counts. Whichever lands second must not restate the other's ordering or status vocabulary — the recurring failure on this surface, and the reason [[FEAT-0089]] exists.

## Acceptance

- [x] A `draft` requirement is marked as awaiting approval where it already sits, nested under its feature — `_owed_flag` on `_requirement_child_item`; `REQ-0029..0032` marked today ([[TASK-0376]])
- [~] A feature at `acceptance: requested` is marked and offers the run's entry point — **marked, but the entry point is not built**: [[FEAT-0063]]'s acceptance runner does not exist, and a door to nothing teaches the reader the feature works. The mark and the badge are real; the run is [[PHASE-024]]'s
- [x] Both are counted in the view's badge and come from the registry, not from a local list — read from `obligations`, never re-derived; the badge counts *notes* while the tree highlights *rows*, and `test_the_badge_counts_notes_while_the_tree_counts_rows` pins the relationship so the difference reads as an explanation rather than a bug
- [x] Approving does not satisfy any close-out gate — [[ADR-0007]]'s separation survives: `stamp_review` refuses gate-bearing note types, and the human-transition table writes `approved`, never `plan-accepted`
- [x] A `changes-requested` feature or task is visible in the tree without a second list anywhere — the row carries the mark; there are zero genuinely-owed verdicts in this corpus ([[ISS-0121]]), and [[FEAT-0090]] asserts no second list exists

## Links

- Decision: [[ADR-0020-Obligations-Live-With-Their-Subject]]
- Paths: `src/project_os_cockpit/cockpit.py` (`_features_groups`, `_requirement_child_item`), `desktop/src/renderer/renderer.ts`

## Closed 2026-08-10

Landed with [[TASK-0376]] and closed here after [[FEAT-0090]]'s walk confirmed the third row of [[ADR-0020]]'s table — *`changes-requested` re-review → the view owning each note's type* — is answered by these marks and by no second list.

**One criterion reconciled rather than ticked.** A feature at `acceptance: requested` is marked, but the run's entry point is not built, because [[FEAT-0063]]'s runner does not exist. Offering a door to nothing is worse than offering none: it teaches the reader the feature works. [[FEAT-0086]] gave that runner its home in the Tests view; building it is the next release.

The finding worth keeping: **the features badge reads 4 while the tree highlights more rows**, because a requirement nests under every feature it specifies. Both are correct — the badge counts notes. Pinned by a test so the next reader gets an explanation rather than a guess.
