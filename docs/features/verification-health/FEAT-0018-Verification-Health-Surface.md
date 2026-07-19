---
type: "[[feature]]"
id: FEAT-0018
aliases: ["FEAT-0018"]
title: "Verification health surface — validator status, drift panel, waiver/review badges"
status: in-review
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-07-05
updated: 2026-07-17
goal: "Make the project-os verification state visible while browsing: a live health badge backed by tools/scripts/validate-docs.py, a drift panel deep-linking each violation to the offending note, and badges for verification waivers, review verdicts, and test adequacy."
related: ["[[FEAT-0017-Overview-Dashboard]]"]
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
