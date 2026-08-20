# Plan — a release says what is in it

[[FEAT-0142-A-Release-Says-What-Is-In-It]], parked in [[PHASE-999-Future]]. **Not scheduled**, and deliberately not broken into tasks yet.

## All three questions are answered; one gate remains

The feature note's three open questions were answered on 2026-08-20 — the mechanism is a checkbox list in the release document, selection **subtracts** from the gate rather than scoping it, and a `done` feature held back is *in the build and not verified here* rather than deferred. The rule is [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]].

**Still no tasks, for one reason only: ADR-0040 reads `proposed`.** That is the same gate [[ADR-0030]], [[ADR-0034]] and [[ADR-0037]] each used — the phase is documented in full and nothing is built. What changed is that the uncertainty is now a decision waiting for a yes, not a question waiting for an answer.

## A prerequisite that is not this feature's to fix

**`your-trainer` has no ledger.** No `docs/releases/ledgers/` directory exists, no verdict has ever been recorded there, and its checks still carry `mark:` in frontmatter. So the `excused` half of [[ADR-0040]] — the half that actually serves *"happy to re-evaluate them for each release … more than likely they will stay open"* — cannot run in the repo that has 59 blocking checks.

Feature selection built on top of that would let somebody deselect a feature to make a number go down, in a repo where the honest alternative (excuse the check, with a reason, expiring at the seal) is unavailable. **That is the ISS-0210 failure mode with an extra step**, and it is the strongest argument for ordering [[ISS-0209]] first.

## The order, when it starts

1. **[[ADR-0040]] accepted.** Nothing before this.
2. **[[ISS-0209]] — the ledger reaches the repos that hold checks.** Not part of this feature, and a prerequisite for it being safe rather than merely working.
3. **Server**: the payload distinguishes a **default** from a **decision** — derived rows, chosen rows, and held-back rows with their reasons. The checkbox list is the working state; `features:` is written at the seal.
4. **The subtraction rule**, with its guard built first: a check covering one selected and one deselected feature still gates. That mixed cell is what a subtraction rule gets wrong, and this phase has shipped three checks that could not fire — so it is constructed and watched to fail before the rule is written.
5. **Client**: the contents rows gain the act; the page reads `N features held back · M checks no longer gating`.
6. **`chronic` keeps counting the excluded.** Verified explicitly, because it is the behaviour a naive implementation removes for free.

## What must not happen

**No verdict write path appears on the release page.** [[ADR-0035]] removed one and [[ISS-0210]] is the record of what it cost — sixty live marks on the page reporting the release was blocked, so the fastest way to unblock it was to tick the things saying it was blocked. Scope selection is a fact about the release and belongs to the release note. If the implementation finds itself writing to a check, the design is wrong.
