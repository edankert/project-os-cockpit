---
type: "[[issue]]"
id: ISS-0069
aliases: ["ISS-0069"]
title: "review_verdict has a second, unguarded vocabulary — 10 notes carry `CLOSE`, which QUALITY.md does not define, and nothing rejects it"
status: fixed
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["FEAT-0018's mode-1 visual pass, 2026-07-30 — a verdict-chip rendered grey"]
severity: medium
component: docs-system
related: ["[[ISS-0024-Status-Surfaces-Outside-The-Parity-Guard]]", "[[FEAT-0018-Verification-Health-Surface]]", "[[project-os-dev#ADR-0011]]", "[[ADR-0007]]", "[[ISS-0066-Test-Coverage-Registers-Drift-By-Hand]]"]
tests: []
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
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

**Nothing validates the field's value.** The validator checks *presence* — [[project-os-dev#ADR-0011]]'s REVIEW rule warns when a terminal note has no `review_verdict` — and the `REVIEW` error checks for the specific string `changes-requested`. An arbitrary value passes both: it is not absent, and it is not `changes-requested`, so it reads as a satisfied review.

## Why it matters more than a typo

**These 10 notes count as reviewed on a word nobody defined.** *(Corrected 2026-07-30 while fixing: all 10 carry `reviewed_by: "opus-independent-review"` and a date, so a review demonstrably happened — see the Resolved section. The original wording here said the information was gone, which was too pessimistic. What is unrecoverable is the verdict's meaning, not whether a review occurred.)*

It also makes every count of "how much of the corpus is reviewed" wrong by up to 10 in an unknown direction. That number is load-bearing right now — [[ADR-0007]]'s settlement rests on "62 notes carrying a `review_verdict`", and the independent review of PHASE-010 already narrowed that to "nearer 51" for exactly this reason.

This is [[ISS-0024]] §1 one level up. That was a second *status* vocabulary (`DONE_REQ` keyed on a retired value) drifting because nothing held it to `statuses.py`. This is a second *verdict* vocabulary drifting because nothing holds it to QUALITY.md. Same shape, different field, and the fix has the same shape too.

## How it surfaced

Not by reading the corpus — by rendering it. [[FEAT-0018]]'s mode-1 visual pass showed a `verdict-chip` reading `close` in grey, the fallback colour for a value the chip vocabulary does not recognise. The chip degrading rather than mis-colouring is **correct behaviour**, and it is the only reason this was visible at all.

Worth keeping: the surface caught what the validator could not, which is the inverse of this repo's usual lesson.

## Expected

`review_verdict` carries a defined value, and an undefined one fails rather than reading as a satisfied review.

## Next Actions

- [x] Decide the vocabulary. `approved` | `changes-requested` for close-out review, plus [[ADR-0007]]'s `accepted` / `accepted-amended` / `rejected` for desk acceptance — the two sets are deliberately distinct and both are legitimate, so the check must know which field context it is in
- [x] Add a check: an unrecognised `review_verdict` fails. Landed in this repo's suite rather than the template-owned validator — see *Not done*
- [x] Decide what the 10 `CLOSE` notes should say. They cannot be reconstructed, so the honest options are `approved` (trusting the session) or clearing the field so ADR-0011's deadline applies to them like anything else unreviewed. **Clearing is the more honest default** — a verdict nobody can interpret is not a verdict
- [ ] Consider upstreaming (open): `QUALITY.md` and the review-field convention are template-owned, so every fleet repo can drift the same way

## Notes

Deliberately **not** fixed in the same pass that found it. Rewriting 10 notes' review verdicts is a decision about whether past reviews happened, which is the owner's call and not something to slip into a close-out commit — the same reasoning that kept [[FEAT-0018]]'s and [[FEAT-0045]]'s close-outs out of the planning commit.

## Resolved 2026-07-30 — cleared, and guarded

**Edwin's call: clear the 10.** Done, in the narrowest form that does not destroy evidence.

### What the notes actually showed, which changes the reasoning

All 10 carry `reviewed_by: "opus-independent-review"` and a `review_date` in 2026-07-21..23. **A review demonstrably happened, by a named reviewer, on a known date.** This note's original framing — "`CLOSE` might have been a paste; the information is gone" — was too pessimistic, and it matters: `approved` was a more defensible guess than first stated, because the alternative (no review occurred) is contradicted by the corpus.

So only the uninterpretable value was cleared. `reviewed_by` and `review_date` are **kept**: they are real information, and removing them would destroy evidence rather than correct a claim. Each of the 10 notes gained a short section recording that `CLOSE` was the original value and why it went.

The consequence is intended: those notes are now `merged` without a verdict, so [[project-os-dev#ADR-0011]]'s REVIEW warning applies with the same 2026-10-23 deadline. They join an honest backlog instead of reading as satisfied gates.

### Guarded

`test_review_verdicts_use_a_defined_value` in `tests/test_coverage_registers.py`. The vocabulary is explicit and split by context, as the Next Actions required:

- close-out review (QUALITY.md): `approved`, `changes-requested`
- desk plan-acceptance ([[ADR-0007]]): `accepted`, `accepted-amended`, `rejected`

Empty passes — it means unreviewed, which ADR-0011 already warns about. An undefined value fails. Mutation-verified by reintroducing `CLOSE`.

**The check reads parsed frontmatter, not source, and the first cut got that wrong.** It used a regex and reported a false positive on `review_verdict: approved  # feature rounds 1-3`, swallowing the trailing YAML comment into the value. Rewritten to use the index's parser. Worth recording because it is the same class as the defect being guarded: a check that matched the wrong thing and looked like a finding.

### Not done

The rule lives in this repo's suite, **not** in `tools/scripts/validate-docs.py`. That validator is template-owned and has a bundled copy TST-0019 holds byte-identical; editing it here is what [[ISS-0026]] was filed for. So other fleet repos remain unguarded, and the upstream recommendation in the Next Actions stands — this is a local check for a template-wide convention.

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

The corpus work is right — clearing the value while keeping `reviewed_by`/`review_date` is the correct call, the per-note record of what `CLOSE` was is good practice, and the consequence (ADR-0011's deadline now applies) is named rather than hidden. The parser-not-regex correction is a genuine catch.

**The guard does not do the one thing this note says it does.** `## Resolved` states "The vocabulary is explicit and split by context, as the Next Actions required", and the Next Action reads "the check must know which field context it is in". `test_review_verdicts_use_a_defined_value` defines the two sets and then checks membership in `ALLOWED_VERDICTS = CLOSE_OUT_VERDICTS | DESK_VERDICTS`. It never asks which context a note is in. Mutation-verified: stamping `CHG-20260721-Child-Phase-Placement` — a close-out change note — with `review_verdict: "accepted"` passes. That is exactly the substitution `test_coverage_registers.py:138` says the split exists to prevent ("deliberately distinct so a plan-acceptance stamp can never satisfy the close-out gate").

Reintroducing `CLOSE` does fail the test, so the primary case is genuinely guarded; the claim that is wider than the code is the context split.

**A third context is unaccounted for.** The two `accepted` values in the corpus are design notes (`DES-0003`, `DES-0004`), recorded by `note_writes.stamp_design_verdict` via `DECIDE_TRANSITIONS["design"]` — not ADR-0007 plan acceptance. They pass only because the union is checked. Whatever shape the context split takes, `design` needs to be one of the contexts, or design acceptances will be classified as desk plan acceptances.
