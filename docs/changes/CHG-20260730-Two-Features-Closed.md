---
type: "[[change]]"
id: CHG-20260730-Two-Features-Closed
aliases: ["CHG-20260730-Two-Features-Closed"]
title: "FEAT-0018 and FEAT-0045 closed — the verification-health visual pass finally run, and the inbox checked rather than assumed"
status: merged
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-30
updated: 2026-07-30
source: ["[[PHASE-011-Unproven-Claims]]"]
related: ["[[FEAT-0018-Verification-Health-Surface]]", "[[FEAT-0045-Project-Inbox]]", "[[TST-0016-Validation-Health]]", "[[ISS-0024-Status-Surfaces-Outside-The-Parity-Guard]]"]
tests: ["[[TST-0016-Validation-Health]]"]
reviewed_by: ""
review_date: ""
review_verdict: ""
---

# Two features closed

No code changed. Both features were complete and unclosed, and each was blocked on a check nobody had run.

## FEAT-0018 — the visual pass was the whole blocker

It sat at `review` since 2026-07-17, explicitly *"held at in-review pending a human visual pass of the mode-1 UI"*. That is the stall [[DES-0001]]'s plate 5 named as "a 6-week in-review stall" and used as a justification for the Waiting-on-you list. Six weeks later the pass had still not happened — so it was run, in Chrome, against this repo's own docs at `http://127.0.0.1:8765/`.

All four acceptance criteria met:

1. **Live flip, no reload.** Clean → `data-state="ok"`. A deliberate drift (a temporary note with `command:` set and `status: passing` but no `last_run:` — a `TEST-FIELDS` error plus two consequential `METRICS` errors) took the badge to `data-state="failing"`, text `3`. `performance.getEntriesByType('navigation').length` stayed at `1` throughout, so it arrived over SSE. Deleting the probe returned it to `ok`, also without a reload.
2. **Drift rows deep-link.** The `TEST-FIELDS` row carried `href="/docs/tests/TST-9999-Drift-Probe.md"` and navigated the centre pane to it. `METRICS` rows correctly carry no link — they are snapshot-level.
3. **Chips render.** `waiver-chip` *waived* at `rgb(209,174,123)`, `verdict-chip` *approved* at `rgb(120,186,142)`.
4. **No new Python dependencies**, validator still the single source of validation logic.

A temporary note was used rather than editing a real one: trivially reversible, and it cannot corrupt something the corpus depends on.

**Found while doing it, and it belongs to [[PHASE-011]]:** a `verdict-chip` reading `close` renders grey — the fallback for a value the vocabulary does not recognise. That is the `review_verdict: CLOSE` population (10 notes) surfacing. QUALITY.md's vocabulary is `approved` | `changes-requested`, so `CLOSE` is corpus drift, and the chip degrading to grey rather than mis-colouring it is correct behaviour.

**Still outstanding and not part of this feature's promise:** the desktop (mode-3) renderer has no health badge. Called out as a follow-up at implementation and still true — the payload and SSE event are renderer-agnostic, so porting is additive. Worth knowing that mode 3 shows nothing rather than showing green.

## FEAT-0045 — checked rather than assumed

All three tasks were `done` while the feature sat at `doing`. Verified: `GET /api/inbox` returns `200` with an empty item list — which is this feature's *success condition*, not an absence of evidence; the store/discard routes are registered; the renderer carries the tray after [[TASK-0234]]; `inbox/` is gitignored and empty; and the triage skill plus the LIFECYCLE section exist.

**It closes with `tests: []`, stated plainly rather than dressed up.** The drop/paste path is renderer-and-Electron behaviour — drag events, clipboard, the Electron 32 API change [[ISS-0060]] was filed for — which the automated suite has no surface for; `tests/test_inbox.py` covers the sidecar half. Closed on those plus the manual check, **not** under a `verification_waiver`: the validator does not require one here, and inventing one to look rigorous would be worse than naming what was exercised. Not re-verified today: an actual file drop and an image paste, both verified when TASK-0233 and ISS-0060 landed.

## Why this is one change note

Neither close-out is code, both were gated on a check rather than on work, and both gates were cleared in the same pass. Splitting them would imply two pieces of work happened.
