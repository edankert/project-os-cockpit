---
type: "[[feature]]"
id: FEAT-0018
aliases: ["FEAT-0018"]
title: "Verification health surface — validator status, drift panel, waiver/review badges"
status: done
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-17
goal: "Make the project-os verification state visible while browsing: a live health badge backed by tools/scripts/validate-docs.py, a drift panel deep-linking each violation to the offending note, and badges for verification waivers, review verdicts, and test adequacy."
related: ["[[FEAT-0017-Overview-Dashboard]]", "[[FEAT-0041-Review-Desk]]", "[[TASK-0211-Verification-Panel]]"]
tasks: ["[[TASK-0111]]", "[[TASK-0112]]", "[[TASK-0113]]"]
tests: ["[[TST-0016]]"]
---

# Verification health surface

## Why
project-os now enforces its invariants mechanically (validator at Stop-hook/pre-commit/CI, blocking verification gate, recorded waivers, independent-review verdicts). The hooks enforce and CI backstops, but nothing shows a human the drift state while they browse — the cockpit is the monitoring pane, so verification state belongs in it. This closes the observability gap the 2026 reliability research flags: enforcement without visibility still leaves the human out of the loop.

## Goal
While browsing any project-os repo in the cockpit, the user can see at a glance whether the docs system is healthy, what exactly is drifting if not, and which items carry waivers, failed reviews, or unevidenced guarding tests.

## Scope
1. **Validation health endpoint** (TASK-0111) — the server runs `tools/scripts/validate-docs.py` (import or subprocess; stdlib-only, both are Python) against the browsed repo, caches the report, re-runs on watcher file events, and fans out changes over the existing SSE channel. New `/api/cockpit/validation` returns `{ok, errors: [{code, message, id, rel}], warnings, checked_at}`.
2. **Health badge + drift panel** (TASK-0112) — a green/red badge in the top bar; clicking opens a drift panel listing each violation with its `[code]` and message, deep-linked via the existing ID resolver to the offending note.
3. **Waiver / review / adequacy badges** (TASK-0113) — amber "waived" chip on notes/list rows with `verification_waiver`; green/red chip for `review_verdict: approved | changes-requested`; visual distinction in test views between TST notes with and without adequacy evidence (`adequacy` / `mutation_score`).

## Out of scope
- Running the validator against repos not currently being browsed (multi-project health dashboards can come with the desktop shell).
- Auto-fixing drift from the UI — the cockpit surfaces, agents and humans fix.
- Mutation testing execution — the cockpit renders recorded evidence, it does not produce it.

## Acceptance
- With a clean repo, the badge is green; introducing a deliberate status drift in a note flips it red within the SSE-reload latency, without a page reload.
- Each drift-panel row navigates the centre pane to the offending note.
- A note with `verification_waiver` shows an amber chip in the metadata strip area and in list rows; `review_verdict` renders green/red; TST notes without adequacy evidence are visually distinct in test views.
- Zero new Python dependencies; the validator remains the single source of validation logic (no reimplementation in the cockpit).

## Status (2026-07-17 — in-review)
All three tasks are implemented and `done`; see the per-task Verification sections for the file-level breakdown. Automated coverage is [[TST-0016]] (`tests/test_validation.py`, 11 passed with mutation-run adequacy evidence; full suite 201 passed / 1 skipped), which exercises the endpoint's three states, drift deep-links, debounced SSE fan-out (including burst coalescing), the waiver/verdict/adequacy payload flags, and the metadata-strip chip render; the endpoint was additionally smoke-tested by curl against this repo's own docs (`state: "ok"`, `X-Cockpit-Schema: 3`, health slot present in the served chrome). Held at `in-review` pending a human visual pass of the mode-1 UI: badge green→red flip on live drift without reload, drift-panel row navigation, and chip rendering on waived/verdict/adequacy fixtures. The desktop (mode-3) renderer intentionally has no badge yet — the payload and SSE event are renderer-agnostic, so porting the chrome is a follow-up.

## Relationship to the review desk's verification panel (2026-07-26)

[[TASK-0211-Verification-Panel]] adds a per-scope Verification panel to feature, phase and release renders: the scope's acceptance tests with status, last run and staleness, plus Run affordances into the manual-test runner. It is the same surface family as this feature and deliberately does not duplicate it — this feature owns **project-scope health** (validator state, drift, waiver and review badges), the panel owns **per-scope test evidence**. The record column consumes both: validator state from here, test counts from there. If this feature's badges move or change shape, that panel is the other caller to update.

## Human visual pass — 2026-07-30, mode 1

The pass this feature was held at `review` for, run against this repo's own docs in Chrome at `http://127.0.0.1:8765/`. All four acceptance criteria met.

**1. Badge flips live, without a reload.** Clean repo → `data-state="ok"`, label *"Docs validation: no drift"*. A deliberate drift was then introduced by adding a temporary note (`TST-9999`, `command:` set and `status: passing` with no `last_run:` — a `TEST-FIELDS` error, plus two consequential `METRICS` errors). The badge became `data-state="failing"`, text `3`, label *"Docs validation: 3 violations — click for the drift panel"* — with `performance.getEntriesByType('navigation').length === 1` throughout, so the flip arrived over SSE and not via a page load. Deleting the probe returned it to `ok`, again without a reload.

A temporary note was used rather than editing a real one deliberately: it makes the drift trivially reversible and cannot corrupt a note the corpus depends on.

**2. Drift-panel rows deep-link.** Opening the panel listed each violation with its `[code]` and message. The `TEST-FIELDS` row carried `href="/docs/tests/TST-9999-Drift-Probe.md"`; clicking it navigated the centre pane to that note (`h1` = *"Drift probe"*, document title updated). The `METRICS` rows correctly carry no link — they are snapshot-level, not note-level.

**3. Chips render.** On `TASK-0184` (done under a `verification_waiver`): a `waiver-chip` reading *waived* at `rgb(209,174,123)` (amber) and a `verdict-chip` reading *approved* at `rgb(120,186,142)` (green), both in the metadata strip and in list rows. `TST-0016` carries the adequacy evidence its own suite asserts.

**4. Zero new Python dependencies**, and the validator remains the single source of validation logic — structural, unchanged since implementation, and asserted by [[TST-0016]].

### One observation, not a defect in this feature

A `verdict-chip` reading **`close`** renders grey at `rgb(153,153,153)` — the fallback for a value the chip vocabulary does not recognise. That is the `review_verdict: CLOSE` population (10 notes) surfacing: QUALITY.md's vocabulary is `approved` | `changes-requested`, so `CLOSE` is corpus drift rather than a rendering bug. The chip degrading to grey rather than mis-colouring it is correct behaviour. Recorded here because [[PHASE-011]] is the phase that should decide what to do about those 10 notes.

### Still deliberately outstanding

The **desktop (mode-3) renderer has no health badge.** That was called out as a follow-up when the feature was implemented and remains true: the payload and SSE event are renderer-agnostic, so porting the chrome is additive. It is not a gap in what this feature promised — the acceptance criteria are mode-1 — but anyone reading `state: ok` in mode 3 is reading nothing, because there is nothing to read.
