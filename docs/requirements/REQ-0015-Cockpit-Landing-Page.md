---
type: "[[requirement]]"
id: REQ-0015
aliases: ["REQ-0015"]
title: "Cockpit landing page — root URL renders the cockpit with a SNAPSHOT-driven home"
status: verified
implements: ["[[FEAT-0006]]"]
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-23
source: []
priority: medium
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[REQ-0013]]", "[[TASK-0018]]"]
tests: ["[[TST-0002]]"]
---

# REQ-0015 — Cockpit landing page

## Statement
The root URL `/` SHALL render the cockpit shell (left + centre + right panes), not the current bare auto-index. The centre pane SHALL show a **synthetic home page** derived from `SNAPSHOT.yaml` if one exists at the repo root; if no snapshot is available, fall back to `docs/README.md`; if neither exists, fall back to the existing landing-style summary so the page never 404s.

The synthetic home SHALL surface, at minimum:

- **Project header** — repo name (from the docs root directory) + a one-line description if available.
- **Active focus** — the snapshot's `focus.feature` / `focus.task` / `focus.phase` / `focus.issue`, each rendered as a status-chip-prefixed link to the relevant note.
- **Phase progress** — every `items.phases.*` entry, in `order`, with status chip and a count of features grouped under it.
- **At-a-glance counts** — the snapshot's `metrics.counts` block: features done/total, tasks done/total, tests passing/failing, issues open/triage, risks open, releases total, decisions total.
- **Recent changes** — the most recent ~5 entries from `items.changes`, each as a link with status chip.

The right pane SHALL render an empty-state placeholder when no note is active ("Select a note to see relationships").

## Acceptance Criteria
- Visiting `/` returns the cockpit HTML shell with `cockpit_active = null`, the JS client mounts the left pane mode picker and filter controls in the header, and the centre pane renders the synthetic home (or README fallback).
- The home page surfaces the focus block from `SNAPSHOT.yaml` and links resolve correctly into the rest of the cockpit.
- All counts render even when the metric is zero (e.g. "Issues open: 0").
- Removing or corrupting `SNAPSHOT.yaml` produces the README fallback without a 500 error; removing the README produces the previous landing-style summary.
- Right pane shows the empty-state when there is no active note; selecting a note from the left pane populates it.

## Rationale
The previous behaviour — `/` rendering a bare auto-index without the cockpit chrome — felt jarring: the app's primary chrome materialised only after a click. SNAPSHOT-driven content turns the landing into a working dashboard rather than a list of links: focus, progress, recent activity. README is a sensible fallback for projects that don't yet maintain a snapshot, and the existing landing summary keeps the door open for projects that have neither.

## Traceability
- Implements: [[FEAT-0006]]
- Implemented by: [[TASK-0018]]
- Related: [[REQ-0013]] (cockpit layout)

## Verification
- 2026-05-23: marked `verified` — Cockpit landing page shipped (TASK-0018, CHG-20260508-Cockpit-Home-And-Library).
