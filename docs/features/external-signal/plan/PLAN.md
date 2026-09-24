# Plan — FEAT-0027 External session signal

1. **TASK-0143 (Python first).** Discovery files in desktop mode + tests; poller decay (TS).
2. **TASK-0141.** Hook script generator + managed settings editing in main; tests for the editing logic via a Python twin? No — editing is TS; hook script itself is Python and testable (TST-0015 covers install semantics via generated files).
3. **TASK-0142.** Settings popover + IPC.

## Codex parity follow-up — 2026-09-23

[[TASK-0635]] extends the existing opt-in to Codex after [[TASK-0634]] settles the event adapter. Validate surgical install/remove and duplicate suppression in disposable configuration before offering the setting. Keep the Claude toggle and its consent semantics.

## Handoff, 2026-09-23

Codex lifecycle and external opt-in code is implemented and tested. TASK-0636 and TASK-0637 are complete. The quoted-status parser correction is fixed upstream and synced here. TASK-0633 retains the incomplete live walk; TASK-0634 and TASK-0635 retain their TST-0011 completion gate. Finish that evidence and fresh independent review before closing either feature.
