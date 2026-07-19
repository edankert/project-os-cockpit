---
type: "[[issue]]"
id: ISS-0002
aliases: ["ISS-0002"]
title: "Instrumented .zshrc breaks when the user aliases claude/codex"
status: fixed
severity: high
component: agent-instrument
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
parent: "[[FEAT-0019-Agent-Hook-Ingestion]]"
related: ["[[TASK-0115]]", "[[RISK-0004-Hook-Injection-Surface]]"]
---

# ISS-0002 — zshrc alias collision

## Problem

Opening the cockpit terminal printed `defining function based on alias 'claude'` + `parse error near '()'` from the generated `zdotdir/.zshrc`. Cause: the generated file sources the user's real `~/.zshrc` first; when that file defines `alias claude=…`, zsh expands the alias inside our subsequent `claude() { … }` definition — a parse error that aborts the rest of the file, so neither wrapper gets defined and instrumentation silently dies for the session.

## Fix

The generated `.zshrc` now runs `unalias claude codex 2>/dev/null` before defining the wrapper functions (aliases would also have shadowed the functions at invocation time — zsh resolves aliases before functions — so removing them is required, not just convenient). Trade-off, stated in the generated file's comment: a user's own claude/codex alias customisations don't apply inside the cockpit terminal; outside it nothing changes. Files regenerate on every PTY spawn, so the fix applies to each new terminal without migration.

## Verification

Manual: with `alias claude="claude --foo"` in `~/.zshrc`, a fresh cockpit terminal opens with no parse errors, `type claude` reports a shell function, and hook events flow (TST-0011 step 1).
