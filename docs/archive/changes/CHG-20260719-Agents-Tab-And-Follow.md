---
type: "[[change]]"
id: CHG-20260719-Agents-Tab-And-Follow
aliases: ["CHG-20260719-Agents-Tab-And-Follow"]
title: "Agents centre tab + follow control — fleet survives navigation; following is consentful"
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
impacts: ["desktop follow toggle (rail)", "agent:focus navigation guard", "centre tab strip", "tab-state heartbeat", "status-toast timer"]
issues: ["[[ISS-0011-Follow-Mode-Evicts-Chosen-View]]"]
features: ["[[FEAT-0034-Agents-Tab-And-Follow-Control]]"]
related: ["[[REQ-0020-View-Sovereignty]]", "[[TASK-0158]]", "[[TASK-0159]]"]
---

# Agents centre tab + follow control (FEAT-0034)

## Summary

**TASK-0158 — follow control.** The desktop shell gains a Following/Manual rail toggle (`#follow-toggle`, crosshair icon, `aria-pressed`), persisted per workspace and reflected on switch. The `agent:focus` handler no longer force-navigates: it navigates only when the workspace is Following **and** the user isn't parked on a virtual page they opened; otherwise the jump is offered via a clickable "Agent focus → … · open" toast (REQ-0020). The tab-state heartbeat reports the real follow value instead of hard-coding `following: true`. This fixes ISS-0011 (the ~agents screen being evicted by agent activity). While here, all status toasts were centralised onto one cancellable auto-hide timer so overlapping toasts stop hiding each other early.

**TASK-0159 — centre Agents tab.** Opening the fleet pins a slim two-tab strip at the top of the centre pane: a doc tab (the last real note) + the Agents tab (with a close ×). `navigateTo` is wrapped so every navigation refreshes the strip. While the fleet is pinned and visible, a follow navigation updates the doc tab in the background (a dot marks it) instead of evicting the fleet; clicking the doc tab renders the updated doc and clears the dot; closing the tab returns to the doc. Tab state resets on workspace switch.

## Verification

Driven end-to-end over CDP: follow toggle present/default-following/persists per workspace; Following navigates, Manual and virtual-page states offer the clickable jump instead; the tab strip appears on open with the correct active tab; a follow while on the fleet updates the doc tab (dot) without leaving it; doc-tab click navigates and clears the dot; close returns to the doc. `tsc` clean.

Independent review (opus): the Manual-mode contract now wins over the tab background-nav (a follow while parked on the pinned fleet is ignored, not silently retargeted, when the workspace is Manual). 

Files: `desktop/src/renderer/{index.html,renderer.ts,renderer.css}`.
