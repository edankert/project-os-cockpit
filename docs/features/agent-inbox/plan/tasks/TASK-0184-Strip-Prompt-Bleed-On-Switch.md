---
type: "[[task]]"
id: TASK-0184
aliases: ["TASK-0184"]
title: "Fix: agent strip leaks the previous workspace's last prompt across a workspace switch"
status: done
phase: "[[PHASE-005-Desktop-Shell]]"
owner: user:edwin
created: 2026-07-21
updated: 2026-09-25
source: ["[[ISS-0015]]"]
parent: "FEAT-0030"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0183]]"]
tests: ["[[TST-0011]]"]

---

# TASK-0184 — clear sticky strip state on workspace switch

Fixes [[ISS-0015]]. The agent strip's `stripLastPrompt` (and the `workTransitions` map behind the session "work" tab) are module-level state deliberately kept sticky within a workspace, but the workspace-switch reset in `openWorkspace` doesn't clear them — only `stripSession`/`lastAgentSnap` are reset. So after switching to a project whose current session carries no prompt of its own, the strip renders the previous workspace's prompt.

Fix: in the `openWorkspace` reset block (where `lastAgentSnap = null; showAgentStrip(null, null);` already run), also clear `stripLastPrompt = ''` and `workTransitions.clear()` so the strip and its work tab start clean for the newly-active workspace.

Verification: build the renderer; switch from a workspace with an active-prompt session to one whose session has no `last_prompt`, and confirm the strip no longer shows the first workspace's prompt.

## Verification

Renderer `tsc` build clean; independent Opus review returned CLOSE on the code (correct location in the switch-reset path, no temporal-dead-zone hazard, sticky-within-workspace behaviour preserved, `workTransitions.clear()` NPE-safe, no other cross-workspace strip leak). No automated renderer unit-test surface exists, so this rides FEAT-0019/FEAT-0030's manual-checklist waiver (TST-0011, `status: ready`) rather than a passing automated test — recorded in `verification_waiver`.

## Waiver retired, 2026-09-25

This note was closed on 2026-07-20 under a waiver of [[TST-0011]], the manual live-agent checklist. Edwin ran that checklist live on 2026-09-25 and all 13 rows passed, so the waiver is retired and the gate is met by the test itself.
