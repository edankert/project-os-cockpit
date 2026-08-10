---
type: "[[task]]"
id: TASK-0379
aliases: ["TASK-0379"]
title: "ARCHITECTURE.md becomes a design note, gaining the status table, revisions and review it has never had"
status: backlog
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["Edwin 2026-08-10: 'Happy to make architecture a design type'"]
parent: "[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]"
effort: S
due: ""
depends: []
blocks: []
related: ["[[ISS-0124-Four-Note-Types-Have-No-Status-Table]]", "[[FEAT-0042-Design-Bench]]", "[[ADR-0006-Retire-Delivered-Band]]"]
tests: []
---

# Architecture becomes a design

## Definition of Done
- [ ] `docs/ARCHITECTURE.md` is a `[[design]]` note with a `DES-####` id, carrying the design status table
- [ ] Its `role:` distinguishes it as descriptive rather than a proposal
- [ ] Its content is corrected: the `updated:` date, and whatever the diagram no longer describes
- [ ] The `architecture` type has no remaining members, and [[ISS-0124]]'s list drops from four types to three
- [ ] Every inbound reference to `ARCHITECTURE.md` still resolves — `docs/README.md`, `project-init/SKILL.md` and several CHG notes name it by path
- [ ] It appears in the Intent view as a constraint, and in the design bench like any other design

## Steps
- [ ] Allocate the next `DES` id; keep the file at `docs/ARCHITECTURE.md` if the path references are load-bearing, or move it and fix them — decide which, do not do half
- [ ] Convert the frontmatter to the design shape; `id: ARCH` goes
- [ ] Correct `updated:` — the file says 2026-05-07 while line 80 describes the desktop shell and sidecar, neither of which existed then
- [ ] Read the diagram against the current system before publishing it as a design; it depicts the original Python server

## Notes
Edwin's call, 2026-08-10, in preference to promoting `architecture` to a first-class type. The reasoning: one note in three months is the same evidence pattern that retired the `delivered` band ([[ADR-0006]]) — a type the corpus does not write. Designs already carry everything an architecture document needs and has never had: a status table, revisions with reasons, review verdicts, an HTML artifact slot and a bench to view it in.

**`role:` is what makes this honest.** Designs are proposal-shaped by default; an architecture document is descriptive — it says what *is*, not what *should be*. Accepting one is not the same act as accepting a proposal, and the field exists to carry that difference.

**The diagram is stale and that is the substantive half of this task.** It draws the original Python server — HTTP server, watcher, SSE, renderer — from a repo that is now 17,000 lines with an Electron shell, per-workspace sidecars and agent instrumentation. Converting the type without reading the content would publish a stale document with a fresh status.
