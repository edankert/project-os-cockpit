---
type: "[[task]]"
id: TASK-0418
aliases: ["TASK-0418"]
title: "The push lives with the commits — history marks what is unpublished and carries the action"
status: backlog
owner: unassigned
created: 2026-08-13
updated: 2026-08-13
phase: "[[PHASE-030-Obligations-Go-Home]]"
source: ["Edwin 2026-08-13: 'have the actual push solution in the overview history'"]
parent: "[[FEAT-0100-Unpushed-Work-Needs-A-Person]]"
effort: M
depends: ["[[TASK-0417-Publication-Enters-The-Registry]]"]
blocks: []
related: ["[[DES-0011-Publication-Is-An-Obligation]]", "[[ADR-0020-Obligations-Live-With-Their-Subject]]", "[[FEAT-0055]]", "[[FEAT-0098]]"]
tests: []
---

# The push lives with the commits

[[ADR-0020]]: an obligation surfaces in the view that owns its subject. The subject of *not pushed* is those specific commits, and the overview's history tile and `~history` already draw commits. So the action goes there, beside the thing it publishes — and a person sees **which** work is unpublished, not only how much.

## Definition of Done

- [ ] [[DES-0011]]'s artifact exists and the design leaves `draft` — **captured from the built surface** via `POST /api/design/capture`, not drawn in advance (Edwin, 2026-08-13: *"probably easier to build it and we can change then"*). `DESIGN-ASSET` exempts a draft and nothing else, and `DESIGN-GATE` fires only past the pending band, so the order is legal; the capture endpoint exists for exactly this iterate-then-deposit shape.
- [ ] **Each unpushed commit divider says it is not pushed**, in both the overview tile and `~history` — which share `fillHistory()`, so this is one change. Not a separate boundary element: the unpushed commits are a contiguous run, so per-commit marking gives the boundary for free and a second mechanism could only disagree with the marks beneath it.
- [ ] The result reads as one ladder with the uncommitted band above it — *in flight → saved → published*, top to bottom, in the order those things happen.
- [ ] The push action sits with the run, labelled with what it will publish. Where exactly it attaches — topmost divider or a header over the run — is the artifact's call.
- [ ] **The deploy-remote refusal is not re-implemented.** It has one home, and the code says why: *"a second copy here is how one of them comes to disagree with the other, on the one action in this app that publishes."* This surface calls it.
- [ ] After a successful push the surfaces go quiet together — badge, `Needs you` row, and the history marks — because they read one source, not because three code paths each remembered to clear.
- [ ] The overview band from [[FEAT-0098]] is reconciled: kept, folded into this, or retired with the reason recorded. Two surfaces on one overview saying the same sentence is the duplication [[ISS-0068]] was about.

## Steps

- [ ] Build the artifact against the five regions; take annotations on it.
- [ ] Implement the marking and the action, calling the existing guard.
- [ ] Decide the band's fate and record it.
