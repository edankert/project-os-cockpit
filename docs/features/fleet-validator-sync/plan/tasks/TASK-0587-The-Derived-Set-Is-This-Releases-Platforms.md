---
type: "[[task]]"
id: TASK-0587
aliases: ["TASK-0587"]
title: "A release's derived contents are its own platform's — exclude a foreign platform from `shipping_in`, and leave the Unreleased card alone"
status: done
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
owner: user:edwin
created: 2026-08-30
updated: "2026-08-30"
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
source: ["[[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]]"]
parent: "FEAT-0143"
effort: ""
due: ""
depends: ["TASK-0586"]
blocks: []
related: ["[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[DES-0012-Tests-In-Two-Flows]]"]
tests: []
---

# The derived set is this release's platform's

## What changed

`publication._ships_on(feature_platform, release_platform)` — one predicate, written as an **exclusion of a foreign platform**: a feature leaves a release's contents only when it names a *different* one. Unset, `cross`, `both`, `all`, `shared` and anything unrecognised stay in.

`shipping_in` now uses its `release_id` argument, which had been accepted and unused. `release_payload` takes its derived rows from `shipping_in` instead of from `unreleased_payload`, and its `count` from `len(derived_rows)` rather than the card's fleet-wide total — a heading that disagrees with the rows beneath it is worse than either number alone.

`unreleased_payload` is untouched. Those features **are** unreleased; the card is right and only the offer was wrong.

## Why not equality

The one-line version — *include when the platforms match* — passes the iOS test and silently drops three-fifths of the corpus's cross-platform spellings. `cockpit._platform_match` knows `""`, `shared` and the picked value; measured on `../your-trainer`, `shared` appears **zero** times against 288 empty, 15 `cross`, 3 `all` and 1 `both`. Equality would have removed 303 of 1,432 platform-bearing notes from every release that named a platform.

The direction is the same one `ADR-0040` chose for check subtraction, and for the same reason: a release surface may only ever remove what somebody can point at.

## Guards, and that they can fail

Four tests in `tests/test_release_contents.py`, on a fixture built from the platform values the corpus actually uses rather than imagined ones.

Both plausible mutants were run before this was called done:

- **no filter at all** (the pre-fix behaviour) → `test_an_android_release_is_not_offered_ios_features` fails.
- **`return f == r`** (the naive match) → `test_cross_platform_spellings_are_not_dropped` fails, **and so does the pre-existing `test_a_candidate_is_not_claimed_by_another_release_on_this_platform`** — the equality rule is a regression against a guard that was already there.

## The navigator was a second reader

`cockpit._publication_groups` built the *Next release* group from `unreleased_payload` directly, so the first cut of this task fixed the release page and left the left pane wrong — which is the only thing the reader looks at first. It now goes through `shipping_in` too.

`test_the_navigator_and_the_page_derive_the_same_set` asserts the two agree rather than asserting a number about either, and it fails when the navigator is put back on `unreleased_payload`. The sets it compares were printed and are non-empty on both sides; an equality guard that passes on two empty sets is worse than no guard.

## Effect on `../your-trainer`

`REL-0013` (`platform: android`) stops being offered nine iOS features and `FEAT-0098`. What remains is `FEAT-0037` (unattributable, genuinely unknown), `FEAT-0057` (cancelled) and `FEAT-0101` (`cross`, so it correctly still qualifies) — and the middle one leaves when `superseded`/`cancelled` stop counting as shippable, which `ISS-0261` files separately.

## Independent review, 2026-08-30 — changes-requested

Both mutants named in *"Guards, and that they can fail"* were re-run and both fail as described, including the pre-existing claimed-by-another-release test under the equality rule. Findings: [[ISS-0266]] (the release page itself is unguarded — `A4` passes 2126 tests; and the navigator/page assertion is `A <= B or B <= A`, which tolerates divergence in either direction rather than asserting agreement), [[ISS-0268]] (the placeholder, `create_release`, and `mark_released` as a fourth reader), [[ISS-0270]] (`303 of 1,432`, and the census two columns out by one). The *"Effect on `../your-trainer`"* table reproduces exactly.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
