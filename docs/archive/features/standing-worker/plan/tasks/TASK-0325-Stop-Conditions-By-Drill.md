---
type: "[[task]]"
id: TASK-0325
aliases: ["TASK-0325"]
title: "Stop conditions proven by drill — budget, backoff, validator red, and the human's stop switch"
status: done
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[FEAT-0074-The-Standing-Worker]]"]
parent: "[[FEAT-0074-The-Standing-Worker]]"
effort: M
depends: ["[[TASK-0323-The-Session-Loop]]"]
blocks: []
related: ["[[REQ-0031-The-Loop-Always-Halts]]"]
tests: []
---

# Stop conditions, by drill

## Definition of Done

- Implemented: daily session and wall-clock budgets; two failed close-outs park an item with an issue; three parked items halt; validator red beyond the session halts; the landing card's stop switch halts now.
- Halting files what-and-why into the queue — a halted worker is an obligation on the desk, not an absence.
- **Each condition exercised in a drill**, the drill logged in the feature note — the PHASE-022 rule that a guard unbroken is a guard unbelieved, applied to autonomy's brakes before they are needed in anger.

## Done — 2026-08-11

**Built first, because [[REQ-0031]] says to**: *"Every halt path exercised by drill before any repo runs unattended — brakes are tested before the hill."* So the stop conditions exist before the loop that would need them, and `tests/test_worker.py` drills each one rather than sampling.

Six halt paths, each with its own drill:

| reason | when |
|---|---|
| `stop-switch` | a human asked, from the landing, without shell access |
| `no-delegation` | **the default** — no approved policy, no worker |
| `validator-red` | the record does not validate; working on a broken record compounds it |
| `parked-items` | 3 parked — failure is compounding, not clearing |
| `session-budget` | 12 sessions today |
| `wall-clock` | 30 minutes in one session |

**A human stop outranks every computed halt.** "Somebody said stop" beats any budget, which is the order a person expects and not the order a loop naturally has.

**Every halt carries a reason**, asserted over all of them. A halt with no reason is the quiet this exists to prevent: a system that stopped and a system that merely went silent look identical from outside, and only one of them is fine.

Failure compounds toward stopping, never toward retrying — `should_park` at two failures, halt at three parked.
