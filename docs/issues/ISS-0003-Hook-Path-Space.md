---
type: "[[issue]]"
id: ISS-0003
aliases: ["ISS-0003"]
title: "Hook commands failed silently — unquoted userData path contains a space"
status: fixed
severity: critical
component: agent-instrument
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
related: ["[[ISS-0002-Zshrc-Alias-Collision]]", "[[TASK-0115]]"]
---

# ISS-0003 — hook path space

## Problem

Real Claude Code sessions in the cockpit terminal fed nothing to `/api/agent-hook` — no busy dot, no needs-input, no session records (user report 2026-07-06: "the claude session running in the cli window does not indicate that it needs input or that it has completed"). Diagnosis by bisection: the settings structure, event names, and `async`/`timeout` fields were all fine (`--settings` honours hooks in Claude Code 2.1.201); the generated hook command was the unquoted path `/Users/…/Library/Application Support/project-os-cockpit-desktop/instrument/…/hook-forward.sh` — hooks run through a shell, so every invocation executed `/Users/…/Library/Application` with `Support/…` as an argument and failed silently (hook failures are non-blocking by design).

## Fix

`claudeSettings()` now single-quotes the hook and statusline command paths (`'\''` splicing). Verified end-to-end before shipping: a real `claude -p` run with the quoted config drove the sidecar's agent-state (`source: hook`) and session record. Configs regenerate at every PTY spawn, so the fix applies on the next terminal open.

## Follow-up

This also explains most of "not all projects with claude code open get the status circle" — cockpit-terminal sessions were uninstrumented everywhere. Sessions in *external* terminals remain unsignalled by design (they rely on `cockpit signal`); a standalone agent-state hook shipped via the project-os template is the proposed follow-up.
