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

## Where the row goes — answered by Edwin, 2026-08-13

[[TASK-0417]] left this open because the overview has no navigator and no landing. I listed three candidates and guessed the third. **Edwin meant the second**, and said so by looking for it there: *"I don't see the push message in the needs you section"* — the rail's attention panel, the one with the project cards and the usage block under it, not the navigator group of the same name.

That settles it, and it is the better answer for a reason the guess missed: the attention panel is **cross-workspace**. Publication is the one obligation whose original failure was fleet-shaped — *312 commits across eight repos, nothing mentioning it* ([[FEAT-0055]]) — and measured again on 2026-08-13 the fleet carried unpushed work in three repos at once, two of them not the one on screen.

The concern that made me discount it — *"that panel is agent-state driven; folding registry obligations in would give one heading two sources"* — is already false: the panel gained `record` cards in TASK-0313 for exactly this reason, and those come from the digest, not from agent state.

**A related finding, not this task's to fix:** the digest's `needs_you_count` walks the corpus itself with `_owed_flag` rather than reading the registry. It is a **third** enumeration of what is owed, which is the class of thing [[FEAT-0089]] exists to end, and it is why publication would never have reached that card on its own.

## Also asked for, same message

- *"the x number of commits not pushed and the push button to be in the history section below"* — this task's original subject, unchanged.
- *"btw, this can become a strip instead of this big card"* — the overview's History tile. Recorded as its own step below rather than folded in silently: it is a change to a surface that is not otherwise being touched.

## Definition of Done

- [ ] [[DES-0011]]'s artifact exists and the design leaves `draft` — **captured from the built surface** via `POST /api/design/capture`, not drawn in advance (Edwin, 2026-08-13: *"probably easier to build it and we can change then"*). `DESIGN-ASSET` exempts a draft and nothing else, and `DESIGN-GATE` fires only past the pending band, so the order is legal; the capture endpoint exists for exactly this iterate-then-deposit shape.
- [ ] **Each unpushed commit divider says it is not pushed**, in both the overview tile and `~history` — which share `fillHistory()`, so this is one change. Not a separate boundary element: the unpushed commits are a contiguous run, so per-commit marking gives the boundary for free and a second mechanism could only disagree with the marks beneath it.
- [ ] The result reads as one ladder with the uncommitted band above it — *in flight → saved → published*, top to bottom, in the order those things happen.
- [ ] The push action sits with the run, labelled with what it will publish. Where exactly it attaches — topmost divider or a header over the run — is the artifact's call.
- [ ] **The deploy-remote refusal is not re-implemented.** It has one home, and the code says why: *"a second copy here is how one of them comes to disagree with the other, on the one action in this app that publishes."* This surface calls it.
- [ ] After a successful push the surfaces go quiet together — badge, `Needs you` row, and the history marks — because they read one source, not because three code paths each remembered to clear.
- [x] **The [[FEAT-0098]] band is narrowed, not retired.** Built and looked at, the duplication was immediate and literal: *"7 commits not pushed"* twice on one page, with two Push buttons. The unpushed half is History's now — the obligation surfaces where its subject lives ([[ADR-0020]]) — and the cross-workspace shortcut is the attention card.

  What stays is the half with **no subject to live with**: a repo with no remote has no unpublished commits to mark, because there is nowhere for them to be unpublished *to*. It is also the worse fact, and no count says it — zero would say the opposite.

- [ ] **The attention panel carries a publication card** per workspace with unpublished work — the count, and the action or the refusal. Deploy remotes say what they are and offer no button.

## Steps

- [ ] Implement the attention-panel card (the `Needs you` half Edwin asked for).
- [ ] Implement the marking and the action in History, calling the existing guard.
- [ ] Decide the band's fate and record it.
- [ ] The History tile becomes a strip rather than a card (Edwin's aside) — separate step, because it changes a surface this work is not otherwise altering.
- [ ] Build the artifact against the six regions; take annotations on it.
