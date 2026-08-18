---
type: "[[feature]]"
id: FEAT-0061
aliases: ["FEAT-0061"]
title: "A thought becomes a triaged issue: ⌘N capture into triage, and a triage tray where those judgments get made"
status: done
phase: "[[PHASE-023-Levers-For-The-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-03
source: ["Review 2026-08-03: the human's raw material is thoughts, and the only entry point is composing a prompt; `triage` items have no surface that says these await your judgment"]
goal: "⌘N opens a one-field capture that files an issue at triage; the issues navigator grows a triage tray whose every row offers accept-as-severity or decline in one click."
requirements: []
tasks:
  - "[[TASK-0283-Capture]]"
  - "[[TASK-0284-The-Triage-Tray]]"
release: ""
related: ["[[FEAT-0059-The-Write-Service-Widens]]"]

---

# Quick capture and triage

## Goal

Capture: ⌘N → title field (body optional) → `POST /api/notes/create` → an ISS at `triage`, linked to the current note if one is open. Under three seconds from thought to record. Triage: the issues navigator's top section when triage items exist — `Needs triage · N` — each row carrying the accept-as-severity picker and decline, through the transition path.

## Why capture and triage are one feature

Capture without triage builds a pile; triage without capture has nothing to triage. The pair is the loop: thought → record → judgment, all without a prompt. The ad-hoc-intake skill remains the *agent's* fuller path (dedup, linking, investigation); capture is deliberately dumber — a title now beats a paragraph never, and an agent can be dispatched at the triage row when investigation is worth it.

## Out of Scope

- Capturing any other type. An idea that is really a feature gets promoted by an agent at triage time.
- Auto-deduplication at capture. The tray shows likely siblings (same words) beside the row instead; merging is a judgment.

## Closed 2026-08-10

The loop closes: thought → record → judgment, none of it through a prompt.

⌘N files an issue at `triage` in one field; the tray lifts those issues above the severities; Accept-as-severity, Defer and Decline discharge them in one click plus at most one pick.

**Two criteria on [[TASK-0284]] are reconciled rather than ticked** — sibling hints and dispatch-from-the-row. Both are additions to the row, both need surfaces this feature does not own, and the tray does its job without them.

**One defect worth remembering:** the tray's first cut *added* triage issues above the severities while leaving them in their severity cards. One item, two rows, one screen — [[ISS-0068]] inside a single surface. A count identity now asserts every issue appears exactly once across the whole Issues payload.
