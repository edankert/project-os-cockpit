---
type: "[[task]]"
id: TASK-0127
aliases: ["TASK-0127"]
title: "Overview sessions redesign — live banner, feeds column, virtual detail page"
status: doing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-05
parent: "[[FEAT-0022-Session-Insight-And-Traceability]]"
effort: "M"
depends: ["[[TASK-0124]]"]
blocks: []
related: ["[[TASK-0118]]"]
tests: ["[[TST-0011]]"]
---

# Overview sessions redesign

## Why

The first cut (TASK-0124) appended an accordion-style sessions section at the very bottom of the Overview. Review findings: buried below the recent feed (worst spot for the most time-sensitive data), visually foreign (`<details>` accordions vs the dashboard's feed-row idiom), static while a session is live (Overview only re-renders on file changes, sessions change on hook events), duplicates the activity strip, and gives detail no room to grow.

## Definition of Done
- [x] Live-session banner directly under the hero — agent, state dot, current prompt, ctx/$ meters, undocumented chip, jump-to-terminal button — shown only while a session is live, refreshed via `cockpit:agent-activity` SSE (debounced, banner-only re-render).
- [x] Sessions render as a second column beside Recent activity in the same feed-row idiom (date, agent pill, prompt one-liner, duration/cost, chips); accordion version removed.
- [x] Clicking a session row opens a virtual detail page in the centre pane (`~session/<id>` pseudo-rel): prompts, files touched (docs files link), produced CHG links — with a real history entry so back/forward work.
- [x] Sessions column refreshes (debounced) on agent-activity SSE while Overview is mounted.

## Steps
- [x] `buildLiveSessionBanner` + SSE-driven `refreshOverviewAgentSurfaces`.
- [x] `buildFeedsGrid` two-column section; session feed rows.
- [x] `~session/` branch in `navigateTo` + `renderSessionDetailPage`; skip tab-state heartbeats for pseudo-rels.
- [x] CSS: banner, feeds grid, session rows, detail page; drop `.ov-session` accordion styles.

## Notes

Chosen over alternatives (fold-into-recent-feed, dedicated nav mode) in review on 2026-07-05 — keeps Overview the single dashboard while giving live state prime placement and detail proper room.
