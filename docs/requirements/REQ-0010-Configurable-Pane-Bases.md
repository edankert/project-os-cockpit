---
type: "[[requirement]]"
id: REQ-0010
aliases: ["REQ-0010"]
title: "Any .base file can mount in any cockpit pane (no hardcoded NAV/CONTEXT)"
status: retired
implements: ["[[FEAT-0006]]"]
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-07
updated: 2026-05-23
source: []
priority: high
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[REQ-0009]]", "[[REQ-0011]]"]
tests: []
---

# REQ-0010 — Configurable pane bases

> **Retired (2026-05-08).** Superseded by [[REQ-0013]] (the cockpit's layout is fixed and code-driven now). See [[ADR-0004]].

## Statement
The cockpit SHALL support mounting any `.base` file under the docs root as either the left or the right pane. The filenames `NAV.base` and `CONTEXT.base` are *defaults*, not implementation constants — the codebase MUST NOT special-case those names. Multiple `.base` files MAY mount in a single pane (rendered as tabs).

Configuration is via CLI flags `--cockpit-left=<path>[,<path>...]` and `--cockpit-right=<path>[,<path>...]`, each accepting a `.base` path, a comma-separated list of paths, or the literal `none` to hide the pane. Defaults: `--cockpit-left=docs/__bases__/NAV.base`, `--cockpit-right=docs/__bases__/CONTEXT.base`.

## Acceptance Criteria
- `python -m project_os_cockpit <docs> --cockpit-left=docs/__bases__/Tasks.base` swaps the left pane to the Tasks dashboard with no code changes.
- `python -m project_os_cockpit <docs> --cockpit-right=none` hides the right pane and gives the centre pane the freed width.
- `python -m project_os_cockpit <docs> --cockpit-left=docs/__bases__/NAV.base,docs/__bases__/Issues.base` mounts both bases in the left pane as tabs.
- A grep for the literal strings `NAV.base` and `CONTEXT.base` in `src/project_os_cockpit/` returns matches *only* in default-value definitions and documentation — no logic branches on those names.

## Rationale
Edwin has signalled that the NAV/CONTEXT identifiers may change, and that other `.base` files (Tasks, Issues, Risks, etc.) deserve to be cockpit-mountable. Hardcoding the two names would block that and would make the cockpit fragile to upstream renames.

## Traceability
- Implements: [[FEAT-0006]]
- Verified by: TASK-0010's CLI flag tests + a static check (linter / grep) for hardcoded base names.
