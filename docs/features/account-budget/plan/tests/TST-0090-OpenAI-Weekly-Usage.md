---
type: "[[test]]"
id: TST-0090
aliases: ["TST-0090"]
title: "OpenAI weekly quota source and Usage display"
command: "cd desktop && npm run build && node --test tests/codex-usage.test.mjs tests/account-budget.test.mjs"
covers: ["[[FEAT-0035]]"]
level: integration
owner: user:edwin
created: 2026-09-16
updated: 2026-09-16
related: ["[[FEAT-0035]]", "[[TASK-0628]]"]
---

# OpenAI weekly quota source and Usage display

## Procedure

Build the desktop and run `node --test tests/codex-usage.test.mjs tests/account-budget.test.mjs` from `desktop/`. Verify primary and secondary weekly windows, general versus model-specific buckets, invalid and missing data, protocol initialization, subprocess exit/timeout, and independent Claude/OpenAI rendering with threshold colours and reset dates. Read the live account through the same module without creating a thread.

## Evidence

2026-09-16: `npm run build` passed and all eight focused Node checks passed. The built reader returned `{weekly:{used_percentage:43,resets_at:"2026-09-23T09:05:27.000Z"}}` from the live signed-in account. The actual renderer bundle in an isolated Electron harness displayed both providers and the weekly reset date; capture: `/tmp/cockpit-review-20260916/usage.png` (temporary local evidence).

## Adequacy

The parser assertions fail if primary-only plans are omitted, percentages are inverted, or Spark replaces the general account bucket. The subprocess fixture refuses an out-of-order protocol and sends a split response. Renderer checks fail if OpenAI depends on Claude being present, shares its freshness, loses threshold colours, or retains a cleared allowance. Timeout and early-exit cases must settle as unavailable. The screenshot verifies layout; it does not certify every state of the full desktop.
