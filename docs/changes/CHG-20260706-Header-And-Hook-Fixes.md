---
type: "[[change]]"
id: CHG-20260706-Header-And-Hook-Fixes
aliases: ["CHG-20260706-Header-And-Hook-Fixes"]
title: "Doc header bar with verb buttons + hook-injection fixes (alias collision, path quoting, requirement squares)"
status: merged
owner: user:edwin
created: 2026-07-06
updated: 2026-07-06
impacts:
  - "desktop/src/ipc/agent-instrument.ts (quoted hook paths, alias-safe zshrc)"
  - "desktop/src/renderer/* (doc header bar; top-bar ▶ removed)"
  - "src/project_os_cockpit/cockpit.py (requirement done-vocabulary)"
features: ["[[FEAT-0026-Verb-Polish]]", "[[FEAT-0019-Agent-Hook-Ingestion]]"]
issues: ["[[ISS-0002-Zshrc-Alias-Collision]]", "[[ISS-0003-Hook-Path-Space]]", "[[ISS-0004-Requirement-Squares-Unfilled]]"]
related: ["[[PHASE-007-Agent-Instrumentation]]", "[[TASK-0140]]"]
---

# Doc header bar + the fixes that made instrumentation actually fire

## What shipped

**Doc header bar (TASK-0140).** Every rendered note gets a sticky header: type icon + ID + title + status chip, the docs-relative path (click to copy), and the note's verb buttons — registry-driven and status-filtered, with the default verb emphasised (`▶ Implement`) — dispatching through the normal execute/queue path. The top-bar ▶ button is retired; the page itself is now the dispatch surface.

**ISS-0003 (critical).** Hook commands were generated with the unquoted userData path, which contains a space (`Application Support`) — every hook invocation failed silently, so no real Claude session ever fed the sidecar. Diagnosed by bisection against a live `claude -p` run; fixed with single-quoted command paths and verified end-to-end (`source: hook` state from a real session).

**ISS-0002 (high).** A user `alias claude=…` in `~/.zshrc` caused a parse error in the generated zdotdir `.zshrc` (zsh alias-expands unquoted function names at parse time, before any `unalias` runs). Fixed with quoted function names + unalias; verified against real zsh with and without the alias.

**ISS-0004 (low).** Overview squares for `fulfilled`/`met` requirements rendered unfilled — the phase bucket vocabulary lacked the requirement done-statuses the hero counters already used.

## Verification

Full suite 186 passed, 1 skipped; `tsc` + build clean; hook pipeline proven with a real headless Claude session against the live sidecar. Visual pass of the header rides on TST-0011.
