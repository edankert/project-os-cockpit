---
type: "[[task]]"
id: TASK-0153
aliases: ["TASK-0153"]
title: "External hook adopts the Notification subtype gate — needs-input means the same thing on every path"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
parent: "FEAT-0033"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TST-0015]]"]
tests: []
---

# TASK-0153 — Notification semantics alignment

The tracker promotes `Notification` → needs-input only for `notification_type ∈ {permission_prompt, idle_prompt, elicitation_dialog}`; the external hook's embedded script promotes every Notification — so the file-fallback path over-alarms. Port the subtype gate into the embedded script (app-settings.ts) and extend the TST-0015-style extracted-script tests with gated/non-gated Notification payloads.
