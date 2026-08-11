---
type: "[[task]]"
id: TASK-0296
aliases: ["TASK-0296"]
title: "The criteria parse has one home"
status: done
phase: "[[PHASE-024-Acceptance-Witnessed]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0065-Acceptance-Debt-Surface]]"]
parent: "[[FEAT-0065-Acceptance-Debt-Surface]]"
effort: S
depends: ["[[TASK-0294]]"]
blocks: []
related: []
tests: []
---

# The criteria parse has one home

## Definition of Done

- The runner (TASK-0287), the debt payload and REQ-BOXES read criteria through one shared parse or a fixture-parity guard that breaks when they disagree — the ISS-0023 rule for a new vocabulary.

## Done — 2026-08-11

`src/project_os_cockpit/criteria.py` is the home, created by [[TASK-0287]] and consumed by the runner, the debt payload and the acceptance endpoint alike.

**And the "one home" claim is proven rather than asserted.** The validator cannot import from the package — it is a standalone script so CI can run it from a bare checkout — so `criteria.py` restates `count_acceptance_boxes` and `test_the_parse_is_identical_to_req_boxes_across_the_corpus` compares both parses **requirement by requirement over the whole live corpus** against the real `validate-docs.py`. A second parse that agrees under test is the affordable version of one parse; a second parse that nobody compares is [[ISS-0023]]'s failure.
