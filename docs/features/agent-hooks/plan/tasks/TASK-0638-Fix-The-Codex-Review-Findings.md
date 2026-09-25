---
type: "[[task]]"
id: "TASK-0638"
title: "Fix what the FEAT-0019 and FEAT-0027 review found in the Codex work"
status: "doing"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: "user:edwin"
created: "2026-09-25"
updated: "2026-09-25"
source: ["FEAT-0019 and FEAT-0027 shared independent review, round 1, 2026-09-25"]
parent: "[[FEAT-0019]]"
effort: "S"
depends: []
blocks: []
related: ["[[FEAT-0027]]", "[[ISS-0312]]"]
tests: ["[[TST-0010]]", "[[TST-0015]]"]
---

# Fix what the FEAT-0019 and FEAT-0027 review found in the Codex work

The shared review of the Codex work (`1d16f08`, `9ecdeb6`) returned changes-requested. Its findings are listed in FEAT-0019's `## Review` section. This task fixes the ones about code or documents that work changed.

## Definition of Done

- [x] A test fails when a manual `cockpit signal` no longer clears the hook-fed session table.
- [x] A test fails when a Codex session is given a Claude transcript's cache reading.
- [x] A test fails when the headline session is chosen by recency instead of by `needs-input` over `busy` over `waiting`, on both copies of that ordering.
- [x] A test pins what "Needs you" shows after a busy headline decays: another session's waiting row stays until it goes cold, and a decayed payload with no waiting row shows nothing.
- [x] A child agent's id is length-capped like the other identifiers.
- [x] A multi-file Codex patch never reports a `file` and a `rel` that name different files.
- [x] A failed Return after a pasted Codex prompt puts the prompt back in the queue instead of dropping it.
- [x] The capability register has rows for Codex native-hook instrumentation and the external Codex toggle.
- [x] FEAT-0019's criterion about `~/.codex` and its line about `notify` match what shipped.

## Verification, 2026-09-25

Each new test was checked by removing the code it guards and seeing it fail: six Python breaks in the source (restored from copies, run with `PYTHONDONTWRITEBYTECODE=1`) and two JavaScript breaks in copies of the built files.

- `node --test desktop/tests/*.test.mjs` (after `npm run build`): 245 tests, 243 pass, 0 fail, 2 skipped (the walk corpus tests, which need a Your Trainer payload).
- `.venv/bin/python -m pytest -q -p no:randomly`: 2,204 passed and 1 failed, 6 skipped. The failure was mine from the PHASE-007 close-out (cfb53b0): I had set TST-0010, TST-0015 and TST-0017 to `passing`, and a test that declares a `command:` carries no verdict in its note (ADR-0025). The three notes are restored to their earlier text, and `tests/test_automated_test_holds_no_verdict.py` passes (38).

The interruption test reviewer A saw fail four times in a row passed 23 of 23 runs on a clean tree, alone and in random order with its sibling files.

## Handoff, 2026-09-25, round 2 running

**Done.** Every box is ticked and committed (2448690).

**Next.** One round-2 reviewer is verifying the fixes from `review-packet.py FEAT-0019 --round 2 --since b5577ea`. If it answers *fixed*: set this task `done`, record round 2 on FEAT-0019 and FEAT-0027 and set both `done`, close PHASE-007, and clear the focus. If not, there is no round 3; the disagreement is adjudicated (QUALITY.md).

