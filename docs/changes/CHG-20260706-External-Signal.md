---
type: "[[change]]"
id: CHG-20260706-External-Signal
aliases: ["CHG-20260706-External-Signal"]
title: "External session signal — settings panel with opt-in ~/.claude hook, desktop discovery files, poller decay"
status: merged
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
impacts:
  - "desktop/src/ipc/app-settings.ts (new — settings store, hook script, managed ~/.claude install/uninstall)"
  - "desktop/src/renderer/* (settings popover; the rail gear finally works)"
  - "desktop/src/ipc/agent-state-poller.ts (stale-state decay)"
  - "src/project_os_cockpit/server.py (discovery files now written in desktop mode)"
features: ["[[FEAT-0027-External-Session-Signal]]"]
related: ["[[PHASE-007-Agent-Instrumentation]]", "[[TST-0015]]", "[[RISK-0004-Hook-Injection-Surface]]"]
---

# Claude sessions in any terminal light the dots — if you say so

## What shipped

**Settings panel + opt-in hook.** The rail's settings gear (a disabled placeholder since FEAT-0015) opens a popover with one toggle: "Signal agent state from external terminals". Enabling it writes a Python hook under the app's userData and installs marker-identified entries into `~/.claude/settings.json` (one-time backup beside it; malformed user settings abort untouched; disabling removes exactly ours). This is the consent gate RISK-0004 now records: the app touches `~/.claude` only through this toggle.

**The hook** no-ops outside project-os repos (SNAPSHOT.yaml walk-up). Inside one, it POSTs the raw payload to the workspace's cockpit when `.cockpit/url` names a live one — external sessions then get the FULL pipeline (sessions, prompts, cost, needs-input inbox) — and falls back to writing `.cockpit/agent-state.json` atomically otherwise, so dots work even with no cockpit running for that repo.

**Desktop discovery files.** Desktop sidecars now write `.cockpit/url` like mode 1 (previously suppressed) — which also fixes `cockpit focus` / `cockpit dispatch` from external terminals against the desktop app, previously silently broken.

**Poller decay.** Busy/waiting/needs-input state older than 10 minutes reads as idle at the poller, so external sessions that die without SessionEnd don't burn a dot forever (sidecar-owned state already decayed server-side).

## Why

The template-shipped variant was rejected in review (imposes hooks on collaborators, double-writes sidecar-owned files, no decay owner). This is the user-level design from that review: your explicit toggle, your `~/.claude`, your repos only, sidecar-first with file fallback, decay handled.

## Verification

[[TST-0015]] passing (4 tests over the exact embedded script, including the live-sidecar POST path); discovery-file change covered in the sidecar contract tests; full suite 189 passed, 1 skipped; `tsc` + build clean. Toggle round-trip and rail-dot visuals ride on [[TST-0011]].
