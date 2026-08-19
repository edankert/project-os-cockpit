---
type: "[[issue]]"
id: ISS-0229
aliases: ["ISS-0229"]
title: "`steps_proven` has been sent on every manual test row since ISS-0197 and no renderer has ever read it — an abandoned walk still looks exactly like one nobody started"
status: open
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
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

- [ ] A manual test row shows how many of its steps stand.
- [ ] `steps_proven` leaves `known_unread`.
