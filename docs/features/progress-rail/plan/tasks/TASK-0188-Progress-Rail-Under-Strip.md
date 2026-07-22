---
type: "[[task]]"
id: TASK-0188
aliases: ["TASK-0188"]
title: "Progress rail — second thin row under the collapsed session strip with live type-coloured work blocks"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["[[REQ-0021]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: []
blocks: []
related: ["[[TASK-0163]]", "[[TASK-0184]]"]
tests: []
verification_waiver: "Renderer-only UI; no automated renderer unit-test surface. Validated live via CDP against a real agent session (render across all note types, live block fill on a driven transition, panel enrichment, chevron/rename); independent review on the code."
---

# TASK-0188 — progress rail under the strip

Implements the headline of [[REQ-0021]]. Add `#agent-strip-rail`, a ~14px flex row inside the strip container directly under the main strip line, visible whenever the strip is visible and the session has ≥1 documented work item. Render one block per `sessionWorkIds()` entry in first-touch order (left→right), reusing the overview `.ov-phase-sq` classes: `data-type` from the ID prefix (TASK→task, ISS→issue, FEAT→feature, REQ→requirement, RISK→risk, TST→test, ADR→adr, CHG→change — add the missing `--type-change` colour), `data-bucket="done"` (filled) when the item's latest known status is done-equivalent (`DONE_STATUSES`), outline otherwise, and a pulse class on the item the agent is touching now (most recent touch/transition while live). Click → `navigateTo` the note; `title` tooltip "ID Title (status)". Cap at ~24 blocks with a trailing "+N". Update on `cockpit:status-change` and on session snapshot refreshes; clear on workspace switch (ISS-0015 pattern).

Verification: with a live session touching documented items, the rail shows outline blocks that fill within one SSE round-trip of the note's status going done; blocks navigate on click; the main strip line (state/prompt/ctx/$) is never truncated by the rail; the rail is absent for sessions with no documented work.

## Verification

Built the rail; verified live via CDP against a real session — the rail renders one type-coloured `.ov-phase-sq` per work item (all of task/issue/feature/requirement/risk/test/adr/change/plan mapped correctly), caps at 24 with a `+N`, hides for sessions with no documented work, and a driven status transition (done→doing→done on a work-list item) filled the block to `data-bucket=done` within one SSE round-trip. tsc clean.
