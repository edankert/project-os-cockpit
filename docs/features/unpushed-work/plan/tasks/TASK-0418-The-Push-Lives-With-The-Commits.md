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

- [ ] [[DES-0011]]'s artifact exists and the design leaves `draft`. It has five declared regions and no rendering; `DESIGN-ASSET` exempts a draft and nothing else, and the design gate is [[PHASE-025]]'s.
- [ ] History distinguishes published from unpublished commits, in both the overview tile and `~history`.
- [ ] The push action sits with them, labelled with what it will publish.
- [ ] **The deploy-remote refusal is not re-implemented.** It has one home, and the code says why: *"a second copy here is how one of them comes to disagree with the other, on the one action in this app that publishes."* This surface calls it.
- [ ] After a successful push the surfaces go quiet together — badge, `Needs you` row, and the history marks — because they read one source, not because three code paths each remembered to clear.
- [ ] The overview band from [[FEAT-0098]] is reconciled: kept, folded into this, or retired with the reason recorded. Two surfaces on one overview saying the same sentence is the duplication [[ISS-0068]] was about.

## Steps

- [ ] Build the artifact against the five regions; take annotations on it.
- [ ] Implement the marking and the action, calling the existing guard.
- [ ] Decide the band's fate and record it.
