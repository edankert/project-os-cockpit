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
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "changes-requested"
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

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — changes-requested

The FEAT-0018 half is the best-evidenced close-out in this range: every acceptance criterion was checked against a live surface with specific measured values, the SSE claim was verified by `navigation.length` rather than assumed, and the mode-3 gap is disclosed rather than absorbed. Approved on its own.

**The FEAT-0045 half does not hold, and the reason is worse than the claim being weak.** `docs/features/inbox/` is **gitignored**. `.gitignore:45` carries an unanchored `inbox/`, which matches any directory of that name at any depth — so `FEAT-0045-Project-Inbox.md`, its `plan/PLAN.md`, and `TASK-0232`/`TASK-0233`/`TASK-0234` are not in the repository. Consequences:

- A fresh clone of `main` **fails `validate-docs.py` with 4 errors** (`features_done` 45/44, `features_total` 50/49, `tasks_done` 240/237, `tasks_total` 247/244) because `SNAPSHOT.yaml`'s metrics count a feature and three tasks the clone cannot see. Locally the validator is green, because locally the files are on disk. LIFECYCLE step 7 says this validator also runs in CI.
- The regression predates this range (it arrived with `afc4fa7`, and `74a2187` was already failing a clone with 3 errors), but this range is where a close-out asserted the opposite. §"FEAT-0045 — checked rather than assumed" verified that `inbox/` is gitignored and empty and did not notice that the same pattern hides the feature's own record.
- FEAT-0045 cannot be independently reviewed from the repository at all: the notes are not in the handoff surface. The verdict recorded on that note is therefore also not committable.

Two smaller consistency points on this note: it links `TST-0016` under `tests:` for a change note that states plainly that no code changed and that FEAT-0045 closes with `tests: []`; and the `close`-verdict observation it records was subsequently filed as ISS-0069, which the note does not point at.

**Asked for:** an ISS-* for the `.gitignore` pattern (anchor it to `/inbox/`, or rename the feature directory), then re-close FEAT-0045 once its notes are in git and a clone validates clean.
