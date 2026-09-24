---
type: "[[reference]]"
id: REFERENCE-CODEX-PARITY-VERIFICATION-20260923
title: "Codex parity implementation and verification"
status: active
owner: user:edwin
created: 2026-09-23
updated: 2026-09-23
scope: project
source: ["User request, 2026-09-23", "https://learn.chatgpt.com/docs/hooks", "https://learn.chatgpt.com/docs/app-server"]
related: ["[[ISS-0312]]", "[[TASK-0633]]", "[[TASK-0634]]", "[[TASK-0635]]", "[[TASK-0636]]", "[[TASK-0637]]"]
---

# Codex parity implementation and verification

The implementation now forwards child lifecycle and interruption, submits queued Codex prompts correctly, and offers a separate external-terminal opt-in. Full Claude Code parity remains unverified: the mixed live-agent walk is still open, session usage lacks an observation source, and reviewer budget enforcement remains instruction-only.

## Isolated live run

Codex 0.156.1 ran in the newly built Electron app copied under `/private/tmp/cockpit-parity-yp4h6z76/app`, using disposable userData at `state/project-os-cockpit-desktop`, workspaces `workspace-a` and `workspace-b`, and tmux socket `cockpit-parity-0923`. The copy changes only the tmux socket and app-state location. Production user configuration and running sessions were preserved. The build came from the working tree based on `abd73db`; it is not a released build.

| Case | Observation |
| --- | --- |
| Normal trust | Folder trust and native hook review appeared. No hook-trust bypass flag was used. |
| Approval and completion | A real sandboxed write raised `Codex · wants to use Bash`; approval completed the turn and showed review attention. |
| Legacy notify defect | The baseline exit left a second notify-only approval-reviewer session waiting. New native launchers omit injected notify; ingestion remains compatible with older launchers. |
| Children | Real SubagentStart and SubagentStop carried a parent session and separate child id. Parent state remained busy. |
| Queue and workspace switching | The baseline inserted but did not submit queued text. Separate bracketed paste and Return now produces a new prompt and the expected `QUEUE_FIXED` reply while another workspace is selected. |
| Interruption | Escape holds the queue. At 17:17:49 UTC a late Bash PostToolUse remained needs-input, with one queued item and the interrupted message. A new prompt produced `RECOVERED` and returned to waiting. |
| Reattachment | The same tmux-owned Codex session survived isolated Electron restarts and accepted further prompts. This does not certify dispatch during sidecar startup. |
| External Codex | Enabled the setting through the isolated Settings UI, reviewed hooks, and ran a separate real CLI. Its `EXTERNAL_CODEX_OK` turn appeared as a separate Codex session. |
| Mixed Claude/Codex | Claude 2.1.280 started in the disposable configuration but reported Not logged in. A real waiting-Claude/busy-Codex screen check remains pending. Existing automated mixed-session tests are fixture evidence. |
| Kill switch and History | Existing generated-shell and History tests pass. History was also opened on the final isolated build and q returned to the shell. The live kill-switch result is recorded below. |

Screenshots and JSON observations are retained under the temporary evidence directory. They are diagnostic artifacts, not release-ledger verdicts. The isolated credentials are removed during cleanup.

## Session usage investigation (TASK-0636)

The installed CLI's `codex app-server generate-json-schema` exposes `thread/tokenUsage/updated` with measured token counters and model context-window fields. A separate read-only App Server process successfully read the exact embedded thread id `01a0cf31-d329-7893-ae8a-d37b0e4925af`, but returned status `notLoaded`. `thread/read` returned stored metadata including model/modelProvider fields, not a live token-usage field or event subscription. `account/usage/read` with that thread id returned `threadUsage: null` and null summary values. The disposable home's App Server daemon control socket did not exist.

No thread was started or resumed by this probe. No model request was used to obtain usage. Stored model metadata is available, but this probe does not establish that it stays current after an independently running CLI changes model. Measured live tokens and context occupancy are unsupported by the tested observer arrangement. Account allowance remains the existing separate usage reader. Neither cached-token counters nor account limits establish cache lifetime or future price; keep cache unknown.

This is a bounded unsupported result, not a claim that every possible Codex deployment lacks telemetry. A managed/shared runtime could expose its owned thread events, but that belongs to the deferred PHASE-040 session-ownership decision. Do not introduce a second owner to draw a meter.

## Adapter enforcement (TASK-0637)

All 67 generated artifacts are current and all 13 adapter fixtures pass. Three combined payload probes ran the generated Codex telemetry forwarder and the project dispatcher: a code edit without focus returned HC-001 deny; completion with a failing manual test returned HC-003 deny; a failing fixture validator returned HC-007 block. The forwarder returned an empty decision object and did not override the gate. These are fixture executions with live telemetry delivery, not a real model attempting forbidden edits. The injected failing validator tests dispatch of a validation failure; the actual repository validator is also run separately.

The current tool-hook contract does not offer reliable child identity on every PreToolUse/PostToolUse. Child start/stop identity therefore does not prove HC-010 tool-call budgeting. Keep the independent-review instructions and label the enforcement difference. Snapshot membership is repaired. A direct prompt-hint probe also exposed quoted-status parsing in the shared dispatcher. The parser is now corrected in project-os and synced here, with a regression checking unquoted, double-quoted and single-quoted states.

## Maintenance

Update this note when the live checklist is completed or the supported App Server observer contract changes. Keep the original review as the dated baseline.

Native session exit returned to the original shell. The sidecar session index marks that parent ended and reports no live native sessions after fixture cleanup.

The final direct startup probe reports `TASK-0633 is doing, phase PHASE-007`. The final kill-switch run used a fresh isolated tmux server: `whence -w codex` returned `codex: command` and the shell printed `KILL_SWITCH=1`. Reattaching an existing shell does not replace its inherited environment or wrapper, so the test deliberately used a fresh shell.
