---
type: "[[task]]"
id: TASK-0617
aliases: ["TASK-0617"]
title: "The capability register loses every row that names a removed route, and Deck is told which rows changed"
status: backlog
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

- [ ] These rows in `docs/reference/cockpit-capability-register.md` are corrected, each in the commit that changed the capability:
  - `shell.reader.design` (line 67) — *"design pages: regions, comments, revisions, capture, offer for review, verdict"* — retired, with what replaces it.
  - `api.write.design` (line 108) — the four `/api/design/*` routes — retired, **but say what moved rather than only what went**: a design's Accept and Decline are still there, on the note, through `/api/notes/transition`. A row that reads as though design verdicts disappeared would be wrong, and it is the exact error the first draft of FEAT-0148's table made.
  - `shell.reader.render` (line 65) — drop *"one naming a design with an artifact or variants opens the design bench"*; add that images resolve from `__attachments__` beside the note.
  - `shell.windows` (line 90) — drop the same clause from the deep-link description.
  - `api.infra` (line 111) — drop `/design-asset/` and `/design-asset-at/`; add the viewer's route.
  - `api.read.record` (line 101) — drop `/api/cockpit/design-revisions/` and `/api/cockpit/design-comments/`; keep `/api/cockpit/designs`.
- [ ] A new row for the viewer, with its detection command, per the register's own contract.
- [ ] Every row's detection command re-run, not assumed.
- [ ] `~/Dev/repos/project-os-deck/docs/reference/cockpit-adoption.md` updated in **Deck's** repo, in its own commit, saying which rows were retired and which are new. Deck shares this sidecar, so a retired endpoint is a thing Deck may be calling.

## Steps

- [ ] Check whether Deck calls any of the eight removed endpoints before removing them, not after. `grep -rn "design-asset\|/api/design/" ~/Dev/repos/project-os-deck/` is the check.
- [ ] Update the register in this repo; update the adoption table in Deck's.

## Notes

CLAUDE.md makes this non-optional: *"The register carries the detection command; a commit it lists without a row is drift."* A removal is a capability change like any other.
