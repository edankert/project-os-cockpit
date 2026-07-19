---
type: "[[change]]"
id: CHG-20260719-Ambient-Consolidation
aliases: ["CHG-20260719-Ambient-Consolidation"]
title: "Ambient status consolidation — footer dot removed, Now card demoted, rate-limit pip added"
status: merged
owner: user:edwin
created: 2026-07-19
updated: 2026-07-19
source: []
commit: ""
pr: ""
reviewed_by: "model:claude-opus"
review_date: 2026-07-19
review_verdict: approved
impacts: ["status footer (agent dot removed)", "overview Now card (demoted to one-liner)", "agent strip (rate-limit pip)"]
issues: []
features: ["[[FEAT-0031-Ambient-Status-Consolidation]]"]
related: ["[[TASK-0148]]", "[[TASK-0149]]"]
---

# Ambient status consolidation (FEAT-0031)

## Summary

Coarse agent state now appears once per scope instead of up to four times.

**TASK-0148.** The status-footer agent dot (`#sf-agent`, `refreshFooterAgent`, and its CSS — the styling-incomplete duplicate that lacked a needs-input style) is removed; the footer keeps only sidecar-process health. The Overview "Now" card is demoted from a rich card (which duplicated the strip + attention panel) to a single line summarising the live session or attention count, linking to `~agents`.

**TASK-0149.** The agent strip gains a `5h N%` rate-limit pip (amber ≥80%, reset time in the tooltip) from the `rate_limits.five_hour` statusline data the tracker already stored but never surfaced — the number to check before dispatching more work.

## Verification

CDP: footer has no `#sf-agent`; the strip pip shows `5h 83%` with `.meter-hot`; the Now one-liner shows the live session summary + "open agents ›" and navigates to `~agents`. `tsc` clean; full renderer builds.

Files: `desktop/src/renderer/{index.html,renderer.ts,renderer.css}`.
