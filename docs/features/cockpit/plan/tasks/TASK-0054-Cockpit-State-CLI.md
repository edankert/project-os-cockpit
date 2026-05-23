---
type: "[[task]]"
id: TASK-0054
aliases: ["TASK-0054"]
title: "Cockpit: `cockpit state` + `cockpit history` CLI"
status: done
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-23
updated: 2026-05-23
source: []
implements: ["[[FEAT-0006]]"]
fixes: []
effort: XS
due: ""
depends: ["[[TASK-0053]]"]
blocks: ["[[TASK-0056]]"]
related: ["[[TASK-0049]]"]
tests: []
---

# TASK-0054 — `cockpit state` + `cockpit history`

## Goal
Expose `/api/cockpit/state` to agents through the existing `cockpit` CLI.

## Definition of Done
- [ ] `cockpit state` prints a compact human-readable summary by default.
- [ ] `cockpit state --json` emits the raw JSON for LLM consumption.
- [ ] `cockpit history [--limit N]` prints the recent nav events (default 10).
- [ ] Both subcommands use the same discovery as `cockpit focus` (env var → `.cockpit/url` walk-up).
- [ ] Non-zero exit when no cockpit is running, with a clear message.
