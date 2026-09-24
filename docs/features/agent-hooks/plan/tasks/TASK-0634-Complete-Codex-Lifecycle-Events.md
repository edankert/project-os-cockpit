---
type: "[[task]]"
id: "TASK-0634"
title: "Complete Codex subagent and interruption reporting"
status: "doing"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: "user:edwin"
created: "2026-09-23"
updated: "2026-09-23"
source: ["User request, 2026-09-23", "docs/reference/codex-parity-review-2026-09-23.md"]
parent: "[[FEAT-0019]]"
effort: "M"
depends: []
blocks: ["[[TASK-0635]]"]
related: ["[[ISS-0312]]", "[[RISK-0004]]"]
tests: ["[[TST-0010]]", "[[TST-0011]]"]
---

# Complete Codex subagent and interruption reporting

## Definition of Done

- [x] Verify installed Codex support and payloads for SubagentStart, SubagentStop and Interrupt before registering the events.
- [x] Forward supported subagent events with stable parent/child identity. A child stopping must not mark its parent complete or release the parent dispatch queue.
- [x] Choose interruption state from observed CLI behavior. Interrupted work must not remain busy indefinitely or dispatch queued work before the parent can accept it.
- [x] Add focused hook-generator, ingestion and queue regression checks and repeat affected live lifecycle rows. Record unavailable CLI events as limits rather than fabricated support.

## Steps

- Confirm the installed behavior and capture a minimal reproduction.
- Deliver only this task's bounded result and record verification evidence.
- Update ISS-0312 and the parent plan before moving focus.

## Notes

Start after the first TASK-0633 attempt identifies the baseline; its complete live pass is not a hard dependency on fixing a discovered gap. Keep the current terminal owner and hook trust review. Unknown event fields must not break ingestion.

The source request and scope decision are recorded verbatim in [[ISS-0312]]. [[RISK-0004]] covers schema drift, configuration preservation and event identity. No new dependency or endpoint is authorized by this task.

The baseline walk also found a notify-only session left waiting after its native parent exited. Remove duplicate legacy reporting from new native-hook launches; preserve ingestion compatibility for older launchers. Native approval and Stop reporting were observed before removing the fallback.

A second live finding affects dispatch: while workspace A was selected, the queue delivered its prompt to Codex in workspace B and removed the queue row, but the text remained unsubmitted in the CLI input. Sending prompt text and Return in one PTY write triggers Codex's paste handling. The fix must separate pasted prompt text from submission and verify that a new prompt event actually follows in the live walk.

## Handoff, 2026-09-23

The implementation and repeat live evidence are recorded in [the verification report](../../../../reference/codex-parity-verification-2026-09-23.md). Approval, child events, background workspace dispatch, interruption with late tool completion, recovery, external Codex and shell return have been observed. Automated suites pass. The final native session ended and no longer appears live; History opens the retained tmux screen and q returns to the shell.

TST-0011 remains active. Its complete mixed-Claude/Codex run is not established because the disposable Claude profile reports Not logged in. Keep this task doing until its linked manual gate is satisfied. Before feature close-out, run fresh independent review; the July waiver and review certify only the earlier scope. No user sessions or real configuration were changed.
