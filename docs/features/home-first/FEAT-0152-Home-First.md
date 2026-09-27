---
type: "[[feature]]"
id: FEAT-0152
aliases: ["FEAT-0152"]
title: "Home first — the four facts on the rail and a Dock badge, and a Home screen of three cards replaces the overview's first screen"
status: backlog
phase: "[[PHASE-045-The-Cockpit-In-Layers]]"
owner: user:edwin
created: 2026-09-17
updated: 2026-09-27
source:
  - "[[DES-0015-The-Cockpit-In-Layers]], option C, recommended first"
  - "Edwin 2026-09-17: 'I am not fully convinced, so document it in such a way that we can refine over time'"
goal: "A person opening a project sees what needs them, what is in flight and how far the work has travelled on one screen that loads under 50 KB, and sees the same four facts per project on the rail and on the Dock badge while the window is hidden."
requirements: []
tasks: []
release: ""
acceptance_exception: ""
acceptance: ""
design: "[[DES-0015-The-Cockpit-In-Layers]]"
related:
  - "[[FEAT-0153-Flows-As-Views]]"
  - "[[FEAT-0154-Subject-Threads]]"
  - "[[DES-0008-The-Returning-Human]]"
  - "[[ADR-0025-An-Owed-Row-May-Appear-Twice]]"
  - "[[FEAT-0092]]"
  - "[[FEAT-0094]]"
---

# Home first

**Not started, and not yet accepted.** This is option C of [[DES-0015-The-Cockpit-In-Layers]], scaffolded so the phase has a place to refine it. It leaves `backlog` only when Edwin accepts the design and picks it.

## Goal

Layers L0 and L1 of the design, and nothing below them. The rail square, the fleet page and a new macOS Dock badge carry four facts per project: what needs a person by verb, whether an agent is idle, working or waiting, how many commits are unpushed and how old the oldest is, and whether the release gate is clear or blocked. A Home page replaces the overview's first screen with three cards, Needs you, In flight and Shipping, one sentence for "since you looked" with the Caught up button, and the active phase as one row. The overview's count tiles, phase accordion and history tile keep their pages under a Record link.

## Scope

- One composed payload for Home, built from payloads that already exist: the obligations breakdown, the six landing payloads trimmed to three rows per verb group, the focus block, one feature's task, criteria and check counts, the history's unpublished count and the release gate's counts. Measured budget in the design: about 30 KB against 772 KB today.
- The Needs you card lists one row per verb group, names the newest subject, and offers the registry verb as its only button. Twelve unpushed commits are one row.
- The In flight card shows the focus feature with three labelled bars and the agent's state, name and last tool on one line. Cost, context and cache temperature move to the record.
- The Shipping card shows the publication rung and the gate, with Test, Push and Run as its verbs, and never the list of unreleased features.
- The Dock badge, through Electron's dock API, showing the count decided under D3.
- Out: any change to the navigators (that is [[FEAT-0153-Flows-As-Views]]), to note pages ([[FEAT-0154-Subject-Threads]]), to any write path, or to the mode 1 HTML.

## Acceptance

- Edwin names the next decision, the in-flight item and the release blocker within ten seconds of opening a project, on his real data, without scrolling.
- Home's first paint reads under 50 KB from the sidecar, measured on every repository the shell discovers.
- Every number on Home says what it counts, and a zero is a sentence ("nothing in flight", "no run recorded"), never a `0`.
- The overview's tiles, phases and history are reachable in one click and unchanged.
- The capability register names the new rows.

## Links

- Design: [[DES-0015-The-Cockpit-In-Layers]], Plates 1 and 2.
- Phase: [[PHASE-045-The-Cockpit-In-Layers]], decisions D1 and D3.
- Plan: `plan/PLAN.md`.
