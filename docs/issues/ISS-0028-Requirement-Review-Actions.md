---
type: "[[issue]]"
id: ISS-0028
aliases: ["ISS-0028"]
title: "Requirements offer no review path, their actions ignore status, and the `verify` verb tells the agent to test-gate them — which ADR-0007 forbids"
status: fixed
severity: medium
owner: user:edwin
created: 2026-07-26
updated: 2026-07-26
component: ui
source: ["user-report:2026-07-26"]
related: [ISS-0026]
tests: []
---

# Requirements cannot be reviewed from the cockpit

## Problem

`your-trainer` carries **120 requirements with unresolved acceptance criteria** (validator `REQ-BOXES`, ledgered at the PHASE-0002 promotion). They are visible, and there is no way to act on them: the reviewer offers no verb that does what they need.

Three defects in `agent_actions.py`'s `"requirement"` block, which has only `implement`, `refine` and `verify`:

**1. No review path.** `feature` has a `request-review` verb that files into the review desk (`~review`, FEAT-0041). `requirement` has none, so a requirement can never reach the desk the left pane's **review** mode renders. That is the gap the report names.

**2. No `when:` clauses.** Every other type gates its verbs by status. Requirements do not, so an `implemented` requirement still offers **Implement**, and a `cancelled` one offers all three.

**3. `verify` contradicts ADR-0007.** Its prompt reads:

> "ensure TST notes exist covering each acceptance criterion, run them, and update the requirement's status accordingly."

ADR-0007 is explicit that **requirements are never gated on linked tests** — that clause is why the `verified` status was retired, and the validator exempts requirements from `VERIFY` precisely so this cannot happen. The verb instructs an agent to reintroduce it by hand.

This is [[ISS-0006]]'s defect in a surface that sweep did not reach: the same reverted rule, surviving in a fourth copy. It is the exact failure the single-contract work (FEAT-0014) exists to stop, and good evidence that prose restating a rule will drift wherever it is allowed to exist.

## Expected

- A requirement with unresolved criteria offers a verb that **reconciles them** — tick with evidence, or amend/narrow/supersede per ADR-0006 — and can be sent to the review desk.
- Verbs match status.
- No verb instructs test-gating a requirement.

## Fix

- Add **`reconcile`** (default for `implemented`): walk the acceptance criteria, tick with evidence or reconcile, per ADR-0006. This is the 120-item workflow.
- Add **`request-review`**, at parity with `feature`.
- Rewrite **`verify`** to check criteria against the shipped system, explicitly *not* test status.
- Add `when:` to every requirement verb.

## Resolution (2026-07-26)

All three defects fixed in `agent_actions.py`:

- **`reconcile` (new, default at `implemented`)** — walks the acceptance criteria, ticks with evidence, and amends/narrows/supersedes where the delivered work departed, per ADR-0006. This is the verb the 120 `REQ-BOXES` requirements in your-trainer needed.
- **`request-review` (new)** — parity with `feature`; POSTs to `/api/cockpit/review-request` so a requirement can reach the `~review` desk the left pane renders.
- **`verify` rewritten** — now checks ticked criteria against the shipped system and states plainly that a linked TST note is *evidence for a criterion, not a gate on the requirement*. The old prompt's "ensure TST notes exist … run them, and update the requirement's status accordingly" was the requirement-level test gate ADR-0007 retired.
- **`when:` added to every requirement verb** — an `implemented` requirement no longer offers "Implement".

Three tests: `test_default_when_lists_encode_lifecycle` was **asserting the defect** (`assert "when" not in req["verify"]`) and now asserts the gating; `test_requirement_verbs_do_not_test_gate` and `test_requirement_has_a_review_path` are new guards so the prose cannot drift back.

Worth recording: this is [[ISS-0006]]'s contradiction in a fourth copy, found by a user looking at the UI rather than by any check. It is the strongest argument yet for FEAT-0014's one-copy rule — a rule restated anywhere will drift there.
