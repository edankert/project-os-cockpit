---
type: "[[change]]"
id: CHG-20260916-Show-OpenAI-weekly-account-usage
title: "Show OpenAI weekly account usage"
status: merged
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
source: ["Edwin: Can we have the weekly openai limit shown in the usage section like we do for claude?"]
commit: ""
pr: ""
impacts: ["[[SUR-0003]]"]
issues: ["[[ISS-0312]]"]
features: ["[[FEAT-0035]]"]
related: ["[[TASK-0628]]", "[[TST-0090]]"]
---

# Show OpenAI weekly account usage

## Summary

Usage gains a labelled OpenAI weekly percentage bar and reset date, alongside Claude. OpenAI means the signed-in Codex account allowance, read through its documented app-server account API.

## Impact

- [[SUR-0003]]: Usage shows separate Claude and OpenAI budgets with coloured bars, percentages used, reset times, and freshness.

## Documentation Coverage (All Types Considered)

- features: updated — FEAT-0035 records the provider-specific source and display.
- requirements: not-applicable — existing account-budget scope; no new requirement boundary.
- tasks: new — TASK-0628 implements the weekly OpenAI reading.
- issues: updated — ISS-0312 records this bounded Codex parity improvement; wider work stays open.
- tests: new — TST-0090 covers quota parsing, subprocess failure, and the renderer.
- workflows: not-applicable — no workflow changes.
- decisions: not-applicable — existing Electron IPC boundary and budget display.
- risks: updated — RISK-0004 records app-server contract drift and authenticated local reads.
- changes: new — this note.
- snapshot: updated — active task and reference membership.

## Verification

The desktop build and eight focused tests pass. The live implementation read 43% used from a 10,080-minute primary window, resetting 2026-09-23 at 10:05 Dublin time. The actual renderer in an isolated Electron harness showed the green OpenAI bar beside Claude with separate reading ages. The rebuilt desktop shell was restarted by its verified PID; the tmux terminals survived. Docs-first and documentation validation passed (existing corpus warnings remain).
