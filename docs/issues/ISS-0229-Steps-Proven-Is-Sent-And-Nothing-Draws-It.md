---
type: "[[issue]]"
id: ISS-0229
aliases: ["ISS-0229"]
title: "`steps_proven` has been sent on every manual test row since ISS-0197 and no renderer has ever read it — an abandoned walk still looks exactly like one nobody started"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-20"
severity: low
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0197-The-Runs-Section-Is-Write-Only]]", "[[ISS-0225-A-Nav-Row-Carries-Data-No-Renderer-Draws]]"]
---

# Found by the guard, on its first run

[[ISS-0225]]'s check — *no key the nav sends may be read by nothing* — was written for a defect of mine from today. It immediately found one that is not.

`cockpit.py:4015` emits `steps_proven` on every manual test row, added by [[ISS-0197]] so a row could say **"60 of 107 proven"**:

> *"Before the read-back this row could say a test had 107 steps and nothing about whether any of them held — so a walk abandoned at step 60 looked exactly like one nobody had started."*

**It is read nowhere in `renderer.ts`.** The sentence that justified computing it was never drawn, so the state it describes is still exactly as invisible as before.

## Suggested fix

Draw it beside `steps` on a manual test row — `60/107 proven` — and keep the absence meaningful: the field is omitted when the note carries no run, because *"0 of 107 proven"* and *"never started"* are different sentences and [[ISS-0197]] was careful about that.

Named in the guard's `known_unread` set meanwhile, with this issue as the reason, rather than deleted — the fix is to render it, not to stop sending it.

## Done when

- [x] A manual test row shows how many of its steps stand. — `Run ▸ 60/107`, title `60 of 107 steps proven`. **Absent, not zero**, when the note carries no run: the server omits the field and the renderer keeps `?? null` rather than defaulting to 0, because *"0 of 107 proven"* and *"never walked"* are the two sentences [[ISS-0197]] was careful to separate.
- [x] `steps_proven` leaves `known_unread`. — and deleting the live read now fails `test_no_nav_payload_field_is_sent_and_never_drawn`, which it did **not** at first: see below.

## Fixed 2026-08-20 — and the guard could not have caught the regression

Removing `steps_proven` from `known_unread` did **not** put it under guard. Mutated — live read deleted, comment left in place — and the suite stayed green.

`test_no_nav_payload_field_is_sent_and_never_drawn` decided membership with `k not in src`, **a plain substring search over the whole renderer including comments.** So the comment I had just written explaining the fix satisfied the guard on the fix's behalf. A key merely *named* in a comment has always read as drawn.

That is the seventh over-broad text match this phase and the first one that was **pre-existing** rather than mine — the guard shipped with it, so every key it has ever cleared was cleared on this basis. Comments are stripped now, and the mutant fails.

### What the honest guard found immediately

`review_verdict` is sent on every nav row and appears in `renderer.ts` in **two comments and no code**. Both comments describe reading it as a past *defect*: the field is sticky, so a row reviewed once reads as reviewed forever — [[ISS-0121]], where all ten owed rows were false.

**So the fix is the opposite of this issue's.** The renderer stopped reading it on purpose; the server kept sending it. It is named in `known_unread` with that reason rather than drawn or deleted, because reading the verdict **alone** is what ISS-0121 forbids, not reading it at all — a consumer pairing it with `review_date` would be legitimate.

### The pattern worth keeping

Both findings came from a guard whose *own* mechanism was broken, and neither was visible until the guard was made to mean what it said. Fixing a check is how you find what it was never checking.
