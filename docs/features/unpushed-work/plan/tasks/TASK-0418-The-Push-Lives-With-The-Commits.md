---
type: "[[task]]"
id: TASK-0418
aliases: ["TASK-0418"]
title: "The push lives with the commits — history marks what is unpublished and carries the action"
status: doing
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

- [x] **The attention panel carries the fact, one card per project, and no button.** Corrected on sight: the first cut gave publication a card of its own even when the workspace already had one, reasoning that an agent waiting and work unpublished are two different asks. Edwin: *"you have created 2 cards for the same project… this needs to be changed to one card and there is no need to have the push button there."* One item, one row is the rule this panel already learned ([[ISS-0068]]), and the push belongs where the commits are. A carded workspace gains a line; an uncarded one gets a card of its own.
- [x] **The duplicate on the record card is gone.** It read *"14 items need a person"* over *"since 16h ago · 1 transition · 14 need you"* — fourteen twice, on two adjacent lines. The since-line now omits the clause its own card's message carries.
- [x] **One place for everything this surface says about publication.** Edwin: *"reuse the same place for other messages if no remote has been configured for instance, this should not be displayed in a different place."* So [[FEAT-0098]]'s band is **retired**, not merely narrowed, and `buildPublicationBlock` renders all three states in the same slot: pushable, deploy-only, and no remote at all.
- [x] **The boundary is red and around the run.** The colour was `--accent-link` (blue) and read as a link; it is now `--status-blocked`, which is the red the retired band wore — *"keep the red boundary around it"* was about that band. And it is a box enclosing the header, the unpublished commits and their transition rows, rather than a rule beside them.

## The card's git line carries both rungs, 2026-08-13

Edwin: *"The git line should also include uncommitted items, not using the red color (amber or grey??)."*

So the line reads **in flight, then saved-but-unsent** — the order those things happen, and the order History draws them down the page:

```
2 not committed   11 commits not pushed
     amber              red
```

**Amber, not grey**, of the two he offered: grey is already the colour of the meta and since lines on that card, so grey would have made a live state read as metadata. Amber sits one rung below the red, which is what it is.

**Scoped to the record** — `docs/` and `SNAPSHOT.yaml` — because History's uncommitted band counts exactly that, and two numbers behind one word on two surfaces describing one project is the defect this feature has hit repeatedly. Verified live: History says *"not committed yet · 2 files"*, the card says *"2 not committed"*, `git status` on the same scope says 2.

A consequence worth noting: a repo with **no remote** and work in flight now earns a card, where before it earned nothing. `Your Trainer` showed *"23 not committed"* the moment this landed.

## Steps

- [ ] Implement the attention-panel card (the `Needs you` half Edwin asked for).
- [ ] Implement the marking and the action in History, calling the existing guard.
- [ ] Decide the band's fate and record it.
- [~] **The History tile stays a card.** Declined by Edwin on 2026-08-13 after using it: *"I like the history functionality now, do not change."* Recorded rather than dropped — it was his own suggestion, and the next person to look at that tile should find the answer rather than the question.
- [ ] Build the artifact against the six regions; take annotations on it. **The only thing this task still owes** — the behaviour is accepted, so what remains is depositing the built surface as [[DES-0011]]'s artifact so the design can leave `draft`.
