---
type: "[[feature]]"
id: FEAT-0034
aliases: ["FEAT-0034"]
title: "Agents centre tab + follow control — the fleet view survives; following becomes consentful"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-19
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
goal: "The centre pane gains a slim tab strip when ~agents is open — the doc on one tab, Agents pinned on another — so the fleet view survives navigation and agent activity; follow-mode navigations land on the doc tab without stealing the view. The desktop gains the Following/Manual toggle mode-1 already has (persisted per workspace), and automatic navigation never evicts a deliberately-opened virtual page (REQ-0020)."
requirements: ["[[REQ-0020-View-Sovereignty]]"]
tests: []
tasks: ["[[TASK-0158]]", "[[TASK-0159]]"]
related: ["[[FEAT-0032-Agents-Screen]]", "[[ISS-0011-Follow-Mode-Evicts-Chosen-View]]"]
---

# Agents centre tab + follow control

## Why

The ~agents screen currently takes over the centre pane and is evicted by follow-mode navigations (ISS-0011) — the screen built for watching agents is interruptible by agents. Chosen from the placement options in the 2026-07-19 round-2 review (artifact §1: claude.ai/code/artifact/f3999688-73de-4c36-bcc7-b2511f554ed0): centre tab (option A) over strip-drawer (B), Mission-Control window (C, possible later complement), and right-pane (D, rejected — too narrow).

## Scope

- **TASK-0158 (standalone fix, do first):** Following/Manual toggle in the desktop chrome, mode-1 semantics, persisted per workspace; the `agent:focus` handler respects it and — regardless of the toggle — never navigates away from a `~` virtual page; suppressed jumps stay discoverable via the existing focus toast.
- **TASK-0159:** slim tab strip on the centre pane, shown only while ~agents is open: doc tab (tracks normal navigation/history) + pinned Agents tab; close affordance on the Agents tab; keyboard cycle.

## Out of scope

Mission-Control as a separate window (revisit after living with tabs); tabs for arbitrary docs (this is a two-tab model, not a browser).
