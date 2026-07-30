---
type: "[[issue]]"
id: ISS-0069
aliases: ["ISS-0069"]
title: "review_verdict has a second, unguarded vocabulary — 10 notes carry `CLOSE`, which QUALITY.md does not define, and nothing rejects it"
status: open
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["FEAT-0018's mode-1 visual pass, 2026-07-30 — a verdict-chip rendered grey"]
severity: medium
component: docs-system
related: ["[[ISS-0024-Status-Surfaces-Outside-The-Parity-Guard]]", "[[FEAT-0018-Verification-Health-Surface]]", "[[ADR-0011]]", "[[ADR-0007]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]"]
tests: []
---

# review_verdict has a second vocabulary

## Problem

QUALITY.md's independent-review verdict is `approved` | `changes-requested`. The corpus holds three values:

```
approved            65
CLOSE               10
accepted             2
```

`CLOSE` is not defined anywhere. `accepted` is legitimate — [[ADR-0007]] introduced it for plan acceptance at the review desk, deliberately distinct so a plan-acceptance stamp cannot satisfy the close-out gate. `CLOSE` is neither.

All 10 are CHG notes from 2026-07-21..23:

```
CHG-20260721-Revive-Ended-Session          CHG-20260721-Terminal-Refit-On-Visibility
CHG-20260721-Strip-Prompt-Bleed            CHG-20260721-Unify-Done-Interpretation
CHG-20260721-Child-Phase-Placement         CHG-20260721-Terminal-Force-Resize-On-Show
CHG-20260722-Restart-Console-Action        CHG-20260722-Console-Progress-Rail
CHG-20260723-Session-Status-Changes        CHG-20260723-Focus-Driven-Inflight
```

A three-day window, so almost certainly one session's convention that nothing rejected.

**Nothing validates the field's value.** The validator checks *presence* — [[ADR-0011]]'s REVIEW rule warns when a terminal note has no `review_verdict` — and the `REVIEW` error checks for the specific string `changes-requested`. An arbitrary value passes both: it is not absent, and it is not `changes-requested`, so it reads as a satisfied review.

## Why it matters more than a typo

**These 10 notes count as reviewed and are not.** Or rather: nobody can tell. `CLOSE` might have meant approved, or "closed without review", or been a paste. The information is gone, and the notes assert a satisfied gate either way.

It also makes every count of "how much of the corpus is reviewed" wrong by up to 10 in an unknown direction. That number is load-bearing right now — [[ADR-0007]]'s settlement rests on "62 notes carrying a `review_verdict`", and the independent review of PHASE-010 already narrowed that to "nearer 51" for exactly this reason.

This is [[ISS-0024]] §1 one level up. That was a second *status* vocabulary (`DONE_REQ` keyed on a retired value) drifting because nothing held it to `statuses.py`. This is a second *verdict* vocabulary drifting because nothing holds it to QUALITY.md. Same shape, different field, and the fix has the same shape too.

## How it surfaced

Not by reading the corpus — by rendering it. [[FEAT-0018]]'s mode-1 visual pass showed a `verdict-chip` reading `close` in grey, the fallback colour for a value the chip vocabulary does not recognise. The chip degrading rather than mis-colouring is **correct behaviour**, and it is the only reason this was visible at all.

Worth keeping: the surface caught what the validator could not, which is the inverse of this repo's usual lesson.

## Expected

`review_verdict` carries a defined value, and an undefined one fails rather than reading as a satisfied review.

## Next Actions

- [ ] Decide the vocabulary. `approved` | `changes-requested` for close-out review, plus [[ADR-0007]]'s `accepted` / `accepted-amended` / `rejected` for desk acceptance — the two sets are deliberately distinct and both are legitimate, so the check must know which field context it is in
- [ ] Add a validator rule: an unrecognised `review_verdict` is an error, not silence
- [ ] Decide what the 10 `CLOSE` notes should say. They cannot be reconstructed, so the honest options are `approved` (trusting the session) or clearing the field so ADR-0011's deadline applies to them like anything else unreviewed. **Clearing is the more honest default** — a verdict nobody can interpret is not a verdict
- [ ] Consider upstreaming: `QUALITY.md` and the review-field convention are template-owned, so every fleet repo can drift the same way

## Notes

Deliberately **not** fixed in the same pass that found it. Rewriting 10 notes' review verdicts is a decision about whether past reviews happened, which is the owner's call and not something to slip into a close-out commit — the same reasoning that kept [[FEAT-0018]]'s and [[FEAT-0045]]'s close-outs out of the planning commit.
