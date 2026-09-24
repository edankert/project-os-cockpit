---
type: "[[task]]"
id: "TASK-0633"
title: "Walk the complete Codex lifecycle in Electron"
status: "doing"
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: "user:edwin"
created: "2026-09-23"
updated: "2026-09-23"
source: ["User request, 2026-09-23", "docs/reference/codex-parity-review-2026-09-23.md"]
parent: "[[FEAT-0019]]"
effort: "S"
depends: []
blocks: []
related: ["[[ISS-0312]]", "[[RISK-0004]]"]
tests: ["[[TST-0011]]"]
---

# Walk the complete Codex lifecycle in Electron

## Definition of Done

- [x] Record the installed CLI version, Electron build, hook trust path, isolated workspace and userData paths, and exact observations in TST-0011.
- [x] Observe a real Codex prompt, working state, approval, completed turn, second prompt and exit to the same shell. Compare each visible state with its sidecar event.
- [ ] Exercise a waiting Claude session beside busy Codex, queued prompts across workspace switches, app restart and reattachment, an older tmux shell, History and the instrumentation kill switch.
- [x] Keep unobserved or fixture-only rows explicitly pending. A complete live pass requires the real CLI; replay tests cannot attest its hook timing or trust behavior.

## Steps

- Confirm the installed behavior and capture a minimal reproduction.
- Deliver only this task's bounded result and record verification evidence.
- Update ISS-0312 and the parent plan before moving focus.

## Notes

Use bounded real prompts in disposable Electron/workspace state. Preserve running user sessions and configuration. Existing TST-0011 evidence is historical; the July waiver does not certify this follow-up. The lifecycle walk does not require a Codex cache estimate.

The source request and scope decision are recorded verbatim in [[ISS-0312]]. [[RISK-0004]] covers schema drift, configuration preservation and event identity. No new dependency or endpoint is authorized by this task.

## Baseline, 2026-09-23

The real Codex 0.156.1 CLI ran inside a copied Electron build at `/private/tmp/cockpit-parity-yp4h6z76`, with its own userData, tmux socket, two fixture workspaces and disposable Codex configuration. Folder trust and the seven-hook review both appeared. A read-only sandbox write requested approval, and Needs You displayed `Codex · wants to use Bash`. After approval, the CLI replied `PARITY_DONE` and Needs You displayed the completed turn.

Exit returned to the shell but did not clear the project state. The native parent session ended; a second session created only by the legacy notify callback remained waiting. Its record has no native hook marker, transcript or prompts. Evidence is in the temporary `approval-evidence.json`, `exit-baseline.json`, `turn-finished.png`, and fixture `.cockpit/sessions.json`. The complete walk remains open while TASK-0634 repairs this demonstrated fallback defect.

## Handoff, 2026-09-23

The implementation and repeat live evidence are recorded in [the verification report](../../../../reference/codex-parity-verification-2026-09-23.md). Approval, child events, background workspace dispatch, interruption with late tool completion, recovery, external Codex and shell return have been observed. Automated suites pass. The final native session ended and no longer appears live; History opens the retained tmux screen and q returns to the shell.

TST-0011 remains active. Its complete mixed-Claude/Codex run is not established because the disposable Claude profile reports Not logged in. Keep this task doing until its linked manual gate is satisfied. Before feature close-out, run fresh independent review; the July waiver and review certify only the earlier scope. No user sessions or real configuration were changed.

Final fresh-shell kill-switch check passed: `codex: command`, `KILL_SWITCH=1`. Temporary credentials and isolated runtime processes were removed after collecting evidence. The next required input is access to a logged-in Claude test session for the mixed live row; all other unverified checklist rows remain explicitly unclaimed.
