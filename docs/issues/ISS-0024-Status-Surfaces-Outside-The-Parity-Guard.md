---
type: "[[issue]]"
id: ISS-0024
aliases: ["ISS-0024"]
title: "Status surfaces outside TST-0019's guard: DONE_BY_TYPE drifted on `implemented`, and two CSS blind spots let a broken palette pass"
status: fixed
severity: medium
phase: "[[PHASE-011-Unproven-Claims]]"
owner: user:edwin
created: 2026-07-24
updated: 2026-07-24
source: ["independent-review:model:claude-fable-5"]
related: ["[[ISS-0023-Implemented-Status-Band-Drift]]", "[[TST-0019-Status-Vocabulary-Parity]]"]
reviewed_by: "model:claude-opus-5"
review_date: 2026-07-30
review_verdict: "approved"
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

## 2. Two CSS constructs still pass a broken palette (FIXED)

Review demonstrated both, each with the suite green:

- **Later same-specificity override** — appending `.status-chip[data-status="staged"] { color: hsl(0, 100%, 50%); }` at the end of `base.css` renders the chip pure red. `_css_status_map` skips any block without `var(--status-…)`, keeps the earlier mapping, and passes.
- **Token redefinition in comma syntax** — `--status-delivered: hsl(340, 90%, 50%)` is hot pink at 90% saturation. `test_status_tokens_stay_muted`'s regex expects space-separated `hsl(H S% L%)`, so the saturation assertion silently skips.

Both are now closed, and both root causes were the same shape: **a check that silently matched nothing counted as a pass.**

- `_css_status_map` did `if not token: continue` — any rule without a `var(--status-…)` was skipped rather than judged, so a literal override was invisible. Replaced by `_css_status_rules`, which returns **every** `[data-status=…]` rule in source order (the cascade is last-wins, so seeing them all is required), plus a new `test_no_literal_colour_on_status_selectors` asserting each `color:` resolves through a palette token.
- `test_status_tokens_stay_muted`'s regex only matched space-syntax `hsl(H S% L%)`. On comma syntax `re.findall` returned `[]`, the loop body never ran, and a 90%-saturated token passed **by matching nothing**. The regex now accepts both syntaxes, and — the real fix — asserts each token was actually found and parsed, so an unmatched token fails instead of passing.

Adequacy proven against five constructs, each of which passed before and fails now:

| Attack | Result |
|---|---|
| Later same-specificity `color: hsl(0, 100%, 50%)` override (the reviewer's exact case) | caught |
| `--status-delivered: hsl(340, 90%, 50%)` comma-syntax hot pink | caught — "is 90% saturated" |
| `color: red` keyword on a group-icon rule | caught |
| Token deleted from `base.css` entirely | caught — "is not defined" |
| `color: #ff0000` hex override | caught |

No false positives: the real stylesheets pass unchanged (252 passed, 1 skipped).

The general lesson, which is the same one that produced the wrong counts elsewhere in this cycle: **an assertion inside a loop over a possibly-empty match set is not an assertion.** Assert the match set is non-empty first.

## 3. `validate_docs_bundled.py` is behind (FIXED)

`validate_docs_bundled.py` still allowed requirement `verified` in `ALLOWED_STATUS`. The canonical `tools/scripts/validate-docs.py` dropped it under ADR-0007; the bundled copy did not follow, so anything validating through the cockpit's fallback path accepted a retired status.

**Fixed**: re-copied verbatim from the canonical validator, and `TST-0019` gains `test_bundled_validator_matches_the_canonical_one` asserting byte-equality — closing the "consider a sync-script check" follow-up left open by `CHG-20260717-Verification-Health-Surface`.

§1–§4 are fixed. §6 (below) is the reason the fixes were invisible in the running app.

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

## 6. The shipped desktop build was never rebuilt — every §4 fix was invisible (FIXED)

Reported by the user after §4 landed: *"I still see the implemented requirements when I hide completed items, and it still shows as a not-filled square."* Both were true, and neither was a logic bug — the fixes were real in source and absent from what was running.

| | |
|---|---|
| `desktop/src/renderer/renderer.ts` | 6 occurrences of `implemented`, edited 22:27 |
| `desktop/dist/renderer/renderer.js` | **0** occurrences, built **09:46** |
| Electron process | running since **09:46** |
| `dist/renderer/*.css` | also from 09:46, so the palette work was missing too |

The Electron app loads `dist/`, produced by `npm run build` (`tsc` + `copy-assets.mjs`). That step was never run, so the mode-3 UI kept enforcing the pre-ADR-0007 vocabulary.

The second symptom has a different path but the same cause: an overview square's fill comes from `PhaseItem.bucket`, computed **server-side** by `is_done_status` in `cockpit.py`. That code was already correct on disk (the bundled Python runtime carries an editable install pointing at `src/`), but the sidecar process had been up since 09:46 with the old module loaded.

**Fixed**: rebuilt (`dist` now carries the current vocabulary and CSS). Requires an app restart to load — both the Electron renderer and the Python sidecars.

**Guarded**: `test_desktop_build_is_not_stale` asserts the shipped bundle contains every status in `COMPLETED_STATUSES` and is no older than its source, skipping when `dist/` is absent (fresh clone / CI without a build). Adequacy proven by stripping `implemented` from the built bundle — the test fails.

**Why the suite did not catch it.** Every other test here reads TypeScript *source*. The artifact that actually runs was unguarded, so 252 green tests coexisted with a stale app. That is the same shape as §2's blind spots and the miscounts elsewhere in this cycle: **the check was pointed at the thing that was correct, not the thing that was used.**

## Closed 2026-07-30

All six findings were already resolved in the code; the status was the only thing left open. Verified before closing rather than taken on the note's word:

| Claimed guard | Present |
|---|---|
| `test_done_by_type_recognises_terminal_requirement_status` | `tests/test_status_vocabulary.py` |
| `test_active_done_is_the_completed_set` | same |
| `test_no_literal_colour_on_status_selectors` | same |
| `test_bundled_validator_matches_the_canonical_one` | same |
| `test_desktop_build_is_not_stale` | same |

And the live bug: `is_done_status("requirement", "implemented")` returns `True`.

§5 stays as recorded — parity-by-construction, noted rather than fixed, because `COLLAPSED_BY_DEFAULT` is an alias of `COMPLETED_STATUSES` and cannot drift. TST-0019's "six surfaces" framing still overstates by one, which is a wording issue in that note rather than a gap here.

Worth naming the pattern this closes into: three items in two days — this, [[FEAT-0018]] and [[FEAT-0045]] — were complete work sitting at a non-terminal status because the *closing* step needs a human and nothing surfaces the backlog of it. That is [[PHASE-011]]'s theme arriving from an unexpected direction: not a claim asserted without evidence, but evidence sitting unclaimed.

One finding from [[FEAT-0018]]'s visual pass belongs to this issue's family and is **not** covered by any guard here: a `verdict-chip` reading `close` renders grey, because `review_verdict: CLOSE` is not in QUALITY.md's `approved` | `changes-requested` vocabulary. 10 notes carry it. The chip degrading rather than mis-colouring is correct, so this is corpus drift, not a surface bug — but it is exactly the "a second vocabulary nobody guards" shape §1 was about, one level up in the review fields rather than the status fields. Filed as [[ISS-0069]].

## Independent review — 2026-07-30 (model:claude-opus-5, fresh context, separate session) — approved

Approved. Closing on a table of "claimed guard → verified present" rather than on the note's own word is the right method for an issue whose findings were fixed in an earlier pass, and I re-checked it: all five named tests exist in `tests/test_status_vocabulary.py`, and `is_done_status("requirement", "implemented")` is `True`. §5 staying recorded-not-fixed is correct — `COLLAPSED_BY_DEFAULT` is an alias of `COMPLETED_STATUSES` and cannot drift — and routing the `close` chip finding to [[ISS-0069]] rather than absorbing it here is the right boundary.

One thing worth knowing, since this issue is the origin of "a second vocabulary nobody guards": the same shape is now live one level down, in `_square_state`. Enumerating `ALLOWED_STATUS` through it, `test`/`failing` maps to no state and no attention dot, so a failing test renders identically to work nobody started — and `DES-0004`'s encoding table has no row for the `blocked` band at all. Recorded against [[ISS-0068]], not reopened here.
