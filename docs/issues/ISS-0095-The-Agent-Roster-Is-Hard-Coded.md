---
type: "[[issue]]"
id: ISS-0095
aliases: ["ISS-0095"]
title: "The dispatchable agent roster is a hard-coded pair, so a standing worker outlives neither a vendor change nor a second opinion"
status: fixed
severity: low
phase: "[[PHASE-027-The-Standing-Worker]]"
owner: user:edwin
created: 2026-08-05
updated: 2026-08-11
source: ["Comparison against t3.codes, 2026-08-05: one ProviderDriver interface with five drivers — Claude, Codex, Cursor, Grok, OpenCode"]
component: server
related: ["[[ADR-0009-The-Principal-Is-A-Role]]", "[[FEAT-0074-The-Standing-Worker]]"]
fixed_by: []
tests: []
---

# The agent roster is hard-coded

## What

`agents.py` declares `AGENTS` as a literal pair — `claude`, `codex` — with `command` and `instrumented` inline. The module already did the hard part (FEAT-0019 collapsed nine restatements into one table, and its docstring anticipates "a third agent"), so this is a small, well-prepared gap rather than a tangle.

T3 Code has one `ProviderDriver` interface behind five drivers (`ClaudeDriver`, `CodexDriver`, `CursorDriver`, `GrokDriver`, `OpenCodeDriver`), each declaring its own executable discovery, environment and capabilities.

## Why it matters more after ADR-0009

[[ADR-0009]] established that **the principal is a role, not a person**. The same argument applies one step down: the *worker* is a role too. A standing worker ([[FEAT-0074]]) that can only ever be Claude Code is a loop with a single point of vendor failure, and it forecloses the cheapest quality mechanism available — running a second opinion from a different model on the same item, which [[ADR-0013]] already blesses for review.

## Fix

Make the roster data, not a literal: id, label, command, instrumented, plus optional discovery and capability hints. A repo's config may extend it. Nothing else changes — `is_dispatchable`, the ledger's wire values and the menu all read the table already.

## Evidence it is fixed

A third agent becomes dispatchable by adding one entry and nothing else; the parity tests that keep the vocabulary in one place still pass.

## Fixed — 2026-08-11

`AgentSpec` gained optional `args` and `role`, and `agents.extend()` merges a repo's own entries over the built-in table. **A third agent is one row and nothing else** — `is_dispatchable`, the ledger's wire values and the dispatch menu all read the table already, which is the part FEAT-0019 had already got right.

Three judgments in the merge, each a way this could be worse than the literal:

- **A half-declared entry is dropped, not shown.** An agent missing `id`, `label` or `command` never reaches the menu, because a dispatch that fails *after* the human has committed to it is worse than an agent that never appeared.
- **A repo entry with an existing id replaces that row**, so a project can change how `claude` is launched without forking the table — and a fork is what it would become the moment it existed.
- **`extend` does not mutate `AGENTS`.** A repo's config leaking into the module-level tuple would carry it into every workspace in the process.

`role` is free text shown in the menu and **nothing keys behaviour off it** — the moment it gated something it would be a second vocabulary.

Why this matters more after [[ADR-0009]], restated because it is the reason this is not cosmetic: the principal is a role, and so is the worker. A standing worker that can only ever be one vendor is a single point of vendor failure, and it forecloses the cheapest quality mechanism available — a second opinion from a different model on the same item, which [[ADR-0013]] already blesses for review.
