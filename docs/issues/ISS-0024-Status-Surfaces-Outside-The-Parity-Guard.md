---
type: "[[issue]]"
id: ISS-0024
aliases: ["ISS-0024"]
title: "Status surfaces outside TST-0019's guard: DONE_BY_TYPE drifted on `implemented`, and two CSS blind spots let a broken palette pass"
status: open
severity: medium
phase: "[[PHASE-007-Agent-Instrumentation]]"
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["independent-review:model:claude-fable-5"]
related: ["[[ISS-0023-Implemented-Status-Band-Drift]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
---

# ISS-0024 — surfaces the parity guard did not cover

[[ISS-0023-Implemented-Status-Band-Drift]] fixed six status surfaces and added [[TST-0019-Status-Vocabulary-Parity]] to stop them drifting again. Independent review found the guard's own blind spots — and one of them had **already drifted, in exactly the way ISS-0023 described**.

## 1. `DONE_BY_TYPE` / `is_done_status` — live bug (fixed)

`src/project_os_cockpit/cockpit.py` carried a second, independent done-vocabulary:

```python
DONE_REQ = {"verified", "met", "fulfilled", "accepted", "retired", "superseded", "cancelled"}
```

It keyed requirement-done on `verified` — retired by ADR-0007 — and omitted `implemented`. Confirmed at runtime: `is_done_status("requirement", "implemented")` returned `False`.

Since `CHG-20260724-Implemented-Rejoins-Done` demoted all 16 of this repo's requirements from `verified` to `implemented`, the cockpit's own progress boxes and work-item done flags (`cockpit.py:335`, `:452`) counted every one of them as unfinished. That is the original ISS-0023 complaint — "implemented requirements never read as completed" — reproduced on a surface the guard did not watch.

**Fixed**: `implemented` added to `DONE_REQ` (`verified` retained so unmigrated repos still read correctly), and `_ACTIVE_DONE` now derives from `statuses.COMPLETED_STATUSES` instead of restating it.

**Guarded**: TST-0019 gains `test_done_by_type_recognises_terminal_requirement_status` and `test_active_done_is_the_completed_set`. Adequacy confirmed by mutation — reverting `DONE_REQ` to the old set fails the new test (1 failed, 14 passed).

## 2. Two CSS constructs still pass a broken palette (open)

Review demonstrated both, each with the suite green:

- **Later same-specificity override** — appending `.status-chip[data-status="staged"] { color: hsl(0, 100%, 50%); }` at the end of `base.css` renders the chip pure red. `_css_status_map` skips any block without `var(--status-…)`, keeps the earlier mapping, and passes.
- **Token redefinition in comma syntax** — `--status-delivered: hsl(340, 90%, 50%)` is hot pink at 90% saturation. `test_status_tokens_stay_muted`'s regex expects space-separated `hsl(H S% L%)`, so the saturation assertion silently skips.

Neither is fixed. Both are narrow (they require someone to add a colour literal rather than a token, which REQ-0012 criterion 1 forbids anyway — but that criterion is a manual grep, not automated). Hardening would be: assert no `color:` declaration on a `data-status` selector resolves to anything but a `var(--status-…)` token, and widen the saturation regex to accept comma syntax.

## 3. `validate_docs_bundled.py` is behind (FIXED)

`validate_docs_bundled.py` still allowed requirement `verified` in `ALLOWED_STATUS`. The canonical `tools/scripts/validate-docs.py` dropped it under ADR-0007; the bundled copy did not follow, so anything validating through the cockpit's fallback path accepted a retired status.

**Fixed**: re-copied verbatim from the canonical validator, and `TST-0019` gains `test_bundled_validator_matches_the_canonical_one` asserting byte-equality — closing the "consider a sync-script check" follow-up left open by `CHG-20260717-Verification-Health-Surface`.

**This issue stays `open`** for §2 above, which is not fixed.

## 4. The Electron desktop renderer had three more unguarded tables (FIXED)

Found on a second sweep, after the first one claimed the cockpit was fully covered. It was not: `desktop/src/renderer/renderer.ts` is the mode-3 UI and carries its **own** status vocabulary, which no test and no Python constant reached. All three tables were stale:

| Table | Was | Effect |
|---|---|---|
| `COMPLETED_STATUSES` (Hide-completed) | `verified`, no `implemented` | every migrated requirement stayed on screen as unfinished — the ISS-0023 symptom, on the desktop |
| `DONE_STATUSES` (session progress views) | same omission | progress blocks never filled for requirements |
| `STATUS_COLOR_BY_KEY` | no `implemented` | fell through to the default ink |

Fixed, and the same pass caught two further disagreements the guard now forbids: the desktop coloured **`accepted`** as done (an ADR's live state — `active` in `statuses.py` and in `base.css`) and put it in Hide-completed, and coloured **`proposed`/`draft`** as active where every other surface says pending.

**Guarded**: three new tests parse `renderer.ts` — completed-set superset + no delivered members, `DONE_STATUSES` covers `implemented`, and every colour key agrees with its band. Adequacy proven by mutation (removing `implemented` from the desktop completed set fails the suite). `base.css` is copied from the Python static dir at build time, so `--status-delivered` needed no separate definition.

**Count correction**: the surface tally is **ten**, not the nine claimed when §1 was written. The desktop was simply never looked at.

## 5. `test_collapsed_by_default_is_terminal_only` is parity-by-construction (noted)

`COLLAPSED_BY_DEFAULT` is defined as an alias of `statuses.COMPLETED_STATUSES` (`templates.py`), so that surface *cannot* drift and the test pins a definition rather than checking an independent literal. Not a defect — but TST-0019's "six surfaces held to it" framing overstates by one.
