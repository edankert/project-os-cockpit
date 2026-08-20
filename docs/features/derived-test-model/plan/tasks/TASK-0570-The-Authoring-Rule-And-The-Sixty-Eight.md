---
type: "[[task]]"
id: TASK-0570
aliases: ["TASK-0570"]
title: "The authoring rule, and the 68 grandfathered by ID"
status: done
phase: "[[PHASE-039-A-Test-Says-Who-Executes-It]]"
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
source: []
parent: "[[FEAT-0140-Sections-Are-Derived-Not-Filed]]"
effort: "M"
due: ""
depends: []
blocks: []
related: []
tests: []
---

# The authoring rule, and the 68 grandfathered by ID

## Definition of Done
- [ ] A newly authored acceptance check with no `covers:` is refused
- [ ] The 68 are listed by ID with a promotion date
- [ ] The list cannot grow — a new violation errors on day one

## Steps
- [ ] Add the check, warning-first with a dated promotion
- [ ] Enumerate the 68 into `GRANDFATHERED.yaml` with reasons
- [ ] Repair the 5 that name an `ISS-*` outside `covers:` by script

## Notes

[[project-os-dev#ADR-0011]]'s clauses apply unweakened: the cutover is in code, no more than 90 days out, and promotion over unpaid debt is forbidden.

Grandfathering **by ID**, never by a blanket exemption — a blanket one silently absorbs instance 69.
