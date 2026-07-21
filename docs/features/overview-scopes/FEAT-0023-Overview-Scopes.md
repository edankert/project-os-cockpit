---
type: "[[feature]]"
id: FEAT-0023
aliases: ["FEAT-0023"]
title: "Overview scopes — drill-down dashboard with pane contract restored"
status: done
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-06
updated: 2026-07-20
reviewed_by: "model:claude-opus"
review_date: 2026-07-20
review_verdict: approved
verification_waiver: "TST-0011 is a manual live-agent e2e checklist; user accepted automated verification in lieu of the manual pass (see 2026-07-20 sweep). Independent review verdict CLOSE."
goal: "Overview mode keeps the app-wide pane contract: the left pane lists scopes (project + phases), selecting one renders that scope's dashboard in the centre (scoped hero, feature squares, exit criteria, scoped activity), and the right pane shows the scope's context plus a live agent Now column — with the mode's lifecycle bugs (history dead-end, re-render churn, fetch fan-out, stale right pane, static live numbers, uncached stats) fixed."
requirements: []
tests: ["[[TST-0012]]", "[[TST-0011]]"]
tasks: ["[[TASK-0128]]", "[[TASK-0129]]", "[[TASK-0130]]"]
related: ["[[FEAT-0017-Overview-Dashboard]]", "[[FEAT-0022-Session-Insight-And-Traceability]]", "[[FEAT-0020-Agent-Activity-Surfaces]]"]
---

# Overview scopes

## Why

Review of the Overview mode (2026-07-06, mockup option D chosen over A/B/C) found the three panes break the app's own contract there: the left nav renders an apology placeholder, the right pane shows stale context from the previously viewed note, and clicking anything that looks like navigation either scrolls (outline metaphor) or yanks you out of the dashboard (note navigation). Everywhere else the panes mean select → detail → context; Overview should too. Making *scope* the selectable unit restores the contract and adds real capability: per-phase exit criteria and per-phase activity have no home anywhere in the cockpit today.

## Scope

1. **Scoped stats endpoint** (TASK-0128). `/api/cockpit/stats?scope=PHASE-####`: hero/status-mix/activity filtered to the phase (phase inheritance via parent feature, as the unscoped payload already does), single phase entry with feature→children squares, `exit_criteria` parsed from the phase note's Exit Criteria checkboxes, `scope` block with id/title/status/rel. Plus a payload cache keyed on index generation (fix 6) so file-event refetches stop re-walking the corpus.
2. **Scope panes** (TASK-0129). Left pane lists Project + phases (mini progress bars, current highlighted); centre renders the scoped dashboard (breadcrumb, open-note link, scoped hero, feature rows, exit criteria, scoped activity) or the project dashboard when Project is selected; right pane shows the scope's linked/backlinks context via the existing context API, topped by the live agent Now card (which replaces the centre live banner) and needs-input entries.
3. **Lifecycle fixes** (TASK-0130). `~overview` / `~overview/PHASE-####` virtual history entries (back/forward reach the dashboard); scroll-preserving refresh on file events instead of full-churn re-render; one shared agent-state fetch feeding strip + Now card + sessions (was 3 fetches per hook event); 30s tick for live durations; right pane never shows stale note context in Overview.

## Out of scope

- Scoping by feature or by platform (phase is the only scope unit in v1; the pattern extends later).
- Editing exit criteria from the dashboard (viewer constraint stands).
- Bento/full-bleed layout changes (option B rejected in review).

## Acceptance

- Selecting a phase in the left pane renders that phase's dashboard in the centre within one fetch; selecting Project restores the all-up dashboard; the app-wide select→detail→context contract holds.
- `~overview/PHASE-007` appears in history: navigate away and back/forward returns to the same scope.
- A file change while Overview is mounted refreshes numbers without losing scroll position.
- One hook event causes at most one `/api/cockpit/state` fetch across strip + Now card + sessions surfaces.
- `stats_payload` is served from cache when the index generation is unchanged (verified by test).
- Exit criteria from the phase note render with checked/unchecked state matching the note.
