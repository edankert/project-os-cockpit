---
type: "[[test]]"
id: TST-0039
aliases: ["TST-0039"]
title: "The check type sits outside the test gates, and each gate is asserted NOT to fire"
status: active
covers: ["[[FEAT-0113-The-Check-Type-And-The-Migration]]"]
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
last_verified: 2026-08-17
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
scope: feature
automated: true
command: ".venv/bin/pytest tests/test_check_type.py -q"
related: ["[[ADR-0030-Acceptance-Checks-Are-Notes-Outside-The-Test-Gates]]"]
---

# The check type sits outside the test gates, and each gate is asserted NOT to fire

Automated, in `tests/test_check_type.py`.

[[ADR-0030]]'s whole argument is that five collisions vanish **by construction** rather than by exemption logic. A test that only asserted the type exists would not check that claim at all — so every assertion here is about a gate *not* firing, and each one names the gate it is about.

## What it pins

**That a `CHK-*` carrying a failed verdict and an untouched `status:` validates.** That is the normal steady state of a suite between walks; if it did not validate, every repo would be red for as long as anything was unwalked.

**That the runner-only rule, the review gate and TEST-ENTRYPOINT never engage.** All three are keyed on something a check cannot hold — `passing` — so the vocabulary itself is the guard, and the test says so by asserting `ALLOWED_STATUS["check"]` and `TEST_RUNNER_STATUSES` are disjoint.

**That `counters.CHK` is enforced.** Driven by lowering the counter and requiring the complaint: without `CHK` in `ID_PREFIXES`, `check_counter` returns before it can compare anything and a corpus could allocate any id it liked.

**That no check ever reaches a badge.** Walked against a real corpus rather than asserted from the registry — the registry saying `none` is a different claim from the payloads carrying nothing.

## Adequacy

Mutation: removing `CHK` from `ID_PREFIXES` fails `test_the_counter_covers_checks`; the rest of the module stays green, which is the point — each assertion is about one gate.
