---
type: "[[task]]"
id: TASK-0617
aliases: ["TASK-0617"]
title: "The capability register loses every row that names a removed route, and Deck is told which rows changed"
status: done
phase: "[[PHASE-042-A-Note-Shows-What-It-Is-About]]"
owner: user:edwin
created: 2026-09-12
updated: 2026-09-12
source: ["CLAUDE.md: 'Every change note that adds, changes or retires capability updates docs/reference/cockpit-capability-register.md in the same commit.'"]
parent: "[[FEAT-0148-One-HTML-Viewer]]"
effort: S
depends: ["[[TASK-0615-Remove-The-Bench]]"]
blocks: []
related: ["[[FEAT-0147-Pictures-Beside-The-Note]]"]
tests: ["[[TST-0087-An-HTML-Page-Opens-In-The-Viewer]]"]
tags: [task, register, deck]
---

# Register and Deck

## Definition of Done

- [x] These rows in `docs/reference/cockpit-capability-register.md` are corrected, each in the commit that changed the capability:
  - `shell.reader.design` (line 67) — *"design pages: regions, comments, revisions, capture, offer for review, verdict"* — retired, with what replaces it.
  - `api.write.design` (line 108) — the four `/api/design/*` routes — retired, **but say what moved rather than only what went**: a design's Accept and Decline are still there, on the note, through `/api/notes/transition`. A row that reads as though design verdicts disappeared would be wrong, and it is the exact error the first draft of FEAT-0148's table made.
  - `shell.reader.render` (line 65) — drop *"one naming a design with an artifact or variants opens the design bench"*; add that images resolve from `__attachments__` beside the note.
  - `shell.windows` (line 90) — drop the same clause from the deep-link description.
  - `api.infra` (line 111) — drop `/design-asset/` and `/design-asset-at/`; add the viewer's route.
  - `api.read.record` (line 101) — drop `/api/cockpit/design-revisions/` and `/api/cockpit/design-comments/`; keep `/api/cockpit/designs`.
- [x] A new row for the viewer, with its detection command, per the register's own contract.
- [x] Every row's detection command re-run, not assumed.
- [x] `~/Dev/repos/project-os-deck/docs/reference/cockpit-adoption.md` updated in **Deck's** repo, in its own commit, saying which rows were retired and which are new. Deck shares this sidecar, so a retired endpoint is a thing Deck may be calling.

## Steps

- [x] Check whether Deck calls any of the eight removed endpoints before removing them, not after. `grep -rn "design-asset\|/api/design/" ~/Dev/repos/project-os-deck/` is the check.
- [x] Update the register in this repo; update the adoption table in Deck's.

## Notes

CLAUDE.md makes this non-optional: *"The register carries the detection command; a commit it lists without a row is drift."* A removal is a capability change like any other.

## Outcome (2026-09-12)

Six rows corrected and one added. `shell.reader.viewer` is the new row; `shell.reader.design` and `api.write.design` are struck through rather than deleted, because a reader of this register needs to know a capability **went** and where its parts landed — `api.write.design` says in as many words that Accept and Decline moved to `api.write.note` rather than disappearing.

**Re-running the detection commands found live code, which is the point of the rule.** Grepping for the retired routes turned up two things the removal had missed: `performNoteAction` still branched on `action.endpoint === '/api/design/verdict'`, and `performDesignVerdict` still fetched `/api/cockpit/design-revisions/` — a request to an endpoint that no longer exists, reachable from a design note's actuator row. Both are gone. A test that pinned that dispatch (`test_the_renderer_reads_the_field_not_the_type`) was rewritten to pin the property that survives: the renderer never asks what type it is holding, which is what made the removal a one-line change.

**Deck:** `project-os-deck` commit `f9f445f`, in Deck's own repo. It had adopted neither retired row and calls none of the five removed write paths — checked by grep over its `desktop/src` before writing it down, not assumed. Its three in-flight files were left alone.

## The variant question this task inherited

`## Variant` sections are still parsed by the sidecar and still emitted as `variants` in `/api/cockpit/designs`, and nothing renders them. **Left in place, deliberately**: the register is a read API Deck shares, removing a field is a narrowing that needs its own notice, and one note in thirteen repos uses the convention. The capability register does not claim a variant surface, because there is none. If it is still unused when something else touches that payload, that is the moment to drop it.
