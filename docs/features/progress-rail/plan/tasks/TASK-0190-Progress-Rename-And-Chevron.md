---
type: "[[task]]"
id: TASK-0190
aliases: ["TASK-0190"]
title: "Rename work tab to progress; replace the files expand button with a rotating chevron"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-22
updated: 2026-07-22
source: ["[[REQ-0021]]"]
parent: "FEAT-0038"
effort: ""
due: ""
depends: ["[[TASK-0189]]"]
blocks: []
related: []
tests: []
verification_waiver: "Renderer-only UI; no automated renderer unit-test surface. Validated live via CDP against a real agent session (render across all note types, live block fill on a driven transition, panel enrichment, chevron/rename); independent review on the code."
---

# TASK-0190 — progress rename + chevron expand affordance

Two cosmetic finishers chosen with the FEAT-0038 design: (1) rename the expanded panel's `work` tab to `progress` — the name the user approved for the filling-boxes mental model (considered: keep `work`, or `session`); (2) replace the strip's expand button — currently the literal text label "files" — with a chevron glyph (⌄) that rotates when the panel is open (CSS transform on `aria-expanded`), keeping the accessible title "Session details". The `files` tab inside the panel keeps its name; only the outer button and the `work` tab change.

Verification: collapsed strip shows the chevron instead of "files"; it rotates when the panel opens; the panel tabs read `progress | files`.

## Verification

Renamed the panel tab `work` → `progress` and replaced the literal 'files' expand button with a `⌄` chevron that rotates on `aria-expanded`. Verified live: expand button text is `⌄`, aria-expanded flips true and rotates, panel tabs read `progress | files`. tsc clean.
