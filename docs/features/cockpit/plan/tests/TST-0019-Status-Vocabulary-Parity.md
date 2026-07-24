---
type: "[[test]]"
id: TST-0019
aliases: ["TST-0019"]
title: "Status vocabulary parity — one canonical band map, six surfaces held to it"
status: passing
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["[[TASK-0198-Delivered-Status-Band]]"]
verifies: ["[[TASK-0198-Delivered-Status-Band]]", "[[ISS-0023-Implemented-Status-Band-Drift]]", "[[REQ-0012-Visual-Style]]"]
path: "tests/test_status_vocabulary.py"
---

# TST-0019 — Status vocabulary parity

## Intent

[[ISS-0023-Implemented-Status-Band-Drift]] was possible because the status vocabulary was restated as six independent literals — two Python tables, a JS object, two CSS rule blocks, and the index collapse set — with nothing tying them together. Fixing the six by hand would have left the next status addition free to drift again. This suite makes `src/project_os_cockpit/statuses.py` the single source of membership and holds the other five surfaces to it, parsing the JS and CSS rather than trusting them.

## Coverage

1. **Vocabulary integrity** — every status belongs to exactly one band; every band has a palette token.
2. **The delivered/completed boundary** — `DELIVERED_STATUSES` and `COMPLETED_STATUSES` are disjoint, `is_completed("staged")` is false and `is_completed("implemented")` is **true** (`implemented` became terminal under ADR-0007; the delivered band now holds `staged`/`monitoring`), and `band_of` is case/whitespace tolerant and returns `None` for unknown values. This is the assertion that keeps ISS-0023 fixed.
3. **Python surfaces** — `cockpit.TASK_STATUS_ORDER` and `templates.STATUS_RANK` each cover the full vocabulary; delivered ranks fall strictly between the pending band's last and the done band's first; `COLLAPSED_BY_DEFAULT` equals the completed set exactly, so `implemented` is never collapsed away.
4. **JS surface** — parses the `COMPLETED_STATUSES` literal out of `static/cockpit.js` (comments stripped) and asserts set equality with the Python constant, plus that it never intersects the delivered band.
5. **CSS surfaces** — parses `.status-chip[data-status=…]` from `base.css` and `.group-icon[data-status=…]` from `cockpit.css` into status→token maps, asserting full vocabulary coverage *and* that each status resolves to its own band's token (a miscoloured status fails, not just a missing one).
6. **Per-type done vocabularies** — no entry in `cockpit.DONE_BY_TYPE` may claim a delivered (non-terminal) status, `is_done_status("requirement", "implemented")` is true, and `_ACTIVE_DONE` equals the completed set. Added after independent review found `DONE_REQ` had drifted exactly this way (ISS-0024).
7. **Bundled-validator sync** — `validate_docs_bundled.py` must be byte-identical to `tools/scripts/validate-docs.py`; it had silently kept the retired requirement `verified` status.
8. **Theme + REQ-0012 constraints** — every band token is defined in both the light and dark blocks, and every semantic hue is ≤60% saturation.

## Evidence

```
$ .venv/bin/pytest tests/test_status_vocabulary.py -q
16 passed in 0.05s

$ .venv/bin/pytest -q
248 passed, 1 skipped
```

Full-suite run includes the superseded contract in `tests/test_index.py::test_implemented_status_sorts_after_backlog_but_stays_expanded`, rewritten from the previous done-band assertion.

## Adequacy

The parity assertions are set-equality, not membership sampling, so adding a status to `statuses.py` without updating a surface fails, and removing one from a surface fails too.

Guard confirmed against the actual defect rather than assumed. **Historical (2026-07-24, when this suite held 13 tests):** with `cockpit.js`, `cockpit.css`, and `cockpit.py` reverted to their pre-fix state and `statuses.py` in place, the suite reported **3 failed, 10 passed** — one failure per drifted surface, naming the exact missing statuses:

```
FAILED test_task_status_order_covers_the_vocabulary
FAILED test_js_completed_set_matches_python
FAILED test_group_icon_css_covers_the_vocabulary_with_the_right_tokens
  AssertionError: no group-icon colour in cockpit.css:
  ['deprecated', 'implemented', 'mitigating', 'monitoring',
   'released', 'resolved', 'rolled-back', 'staged']
```

Not covered: visual rendering of the new amber `--status-delivered` hue in a real browser — that remains a human visual pass, as it was for [[REQ-0012-Visual-Style]] originally.

**Current (16 tests).** Independent review re-verified each guard by mutation rather than by re-reading: poisoning `DONE_REQ` with `staged` fails the delivered/done separation assertion; poisoning `DONE_ISS` with `monitoring` fails the per-type loop (a case the direct assertions do not reach); appending two bytes to `validate_docs_bundled.py` fails the byte-identity guard. All mutations restored byte-identically.

Two blind spots are known and **not** guarded — a later same-specificity CSS override with a colour literal, and a token redefined in comma-syntax `hsl()` which the saturation regex skips. Both were demonstrated live against this suite. Tracked in [[ISS-0024-Status-Surfaces-Outside-The-Parity-Guard]] §2.
