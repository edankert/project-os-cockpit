---
type: "[[feature]]"
id: FEAT-0027
aliases: ["FEAT-0027"]
title: "External session signal — opt-in user hook, settings panel, desktop discovery files"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist (real claude/codex launch, permission prompt, OS notification). User accepted the automated verification in lieu of the manual pass on 2026-07-20: instrumentation-pipeline smoke test (generated scripts → sidecar tracker), CDP UI checks, 409 sidecar-identity guard, 217 passing unit tests, and an independent review verdict of CLOSE for all five."
goal: "Claude sessions in ANY terminal light the rail dots: a cockpit-managed hook installed into the user's ~/.claude/settings.json — gated by an explicit enable/disable toggle in the new cockpit settings panel — POSTs to the workspace sidecar when one runs (full pipeline) and writes .cockpit/agent-state.json directly otherwise; desktop sidecars now write discovery files (fixing cockpit CLI against the desktop app), and the poller decays stale external state."
requirements: []
tests: ["[[TST-0015]]", "[[TST-0011]]"]
tasks: ["[[TASK-0141]]", "[[TASK-0142]]", "[[TASK-0143]]"]
related: ["[[FEAT-0019-Agent-Hook-Ingestion]]", "[[RISK-0004-Hook-Injection-Surface]]", "[[ISS-0003-Hook-Path-Space]]"]
---

# External session signal

## Why

Cockpit-terminal sessions are instrumented (FEAT-0019); external ones are invisible unless the model remembers `cockpit signal`. The template-shipped hook was rejected in review (2026-07-06) for imposing behaviour on collaborators, double-writing the sidecar-owned state file, and leaving stale state undecayed. This is the user-level design that survives those objections: the hook lives in the **user's own** `~/.claude/settings.json`, installed and removed by the cockpit only through an explicit settings toggle (consent gate), defers to a live sidecar when one exists, and the poller owns decay for sidecar-less workspaces.

## Scope

1. **Hook + managed install** (TASK-0141). A generated Python hook under the app's userData: no-op outside project-os repos (SNAPSHOT.yaml walk-up); POSTs the raw payload to the sidecar's `/api/agent-hook` when `.cockpit/url` exists (full pipeline — sessions, cost, inbox); otherwise writes `.cockpit/agent-state.json` atomically (busy/needs-input/waiting/idle mapping, `source: external-hook`). Install/uninstall edits `~/.claude/settings.json` surgically: entries identified by the hook's path, one-time backup to `settings.json.cockpit-backup`, uninstall removes exactly ours.
2. **Settings panel** (TASK-0142). The rail's settings button (a disabled placeholder since FEAT-0015) becomes real: a popover with the "Signal agent state from external terminals" toggle (with an honest description of what it writes where), persisted app-side; toggling installs/uninstalls the hook.
3. **Desktop discovery files + poller decay** (TASK-0143). Desktop sidecars now write `.cockpit/url` like mode 1 (they were suppressed; that also silently broke `cockpit focus/dispatch` from external terminals against the desktop app) and remove it on exit. The poller treats busy/waiting/needs-input state older than the decay window as idle, so external sessions that die without `SessionEnd` don't burn a dot forever.

## Out of scope

- Installing anything without the toggle being flipped by the user.
- Codex external sessions (its notify config is user-global TOML; follow-up).
- Rich data for sidecar-less workspaces (dots only, by design — the POST path provides the full pipeline when a sidecar runs).

## Acceptance

- Toggle on → `~/.claude/settings.json` gains exactly the cockpit's marker-identified entries (backup created once); toggle off → they're gone, everything else untouched (TST-0015).
- With the desktop app running, `claude` in an external terminal under an open workspace lights that repo's dot via the sidecar POST path; under a discovered-but-unopened workspace, via the state-file path.
- `cockpit dispatch`/`focus` from an external terminal now reach desktop sidecars.
- A busy dot from a killed external session decays to idle within the poller's decay window.
