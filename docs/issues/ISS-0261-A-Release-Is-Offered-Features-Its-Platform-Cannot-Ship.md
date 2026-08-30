---
type: "[[issue]]"
id: ISS-0261
aliases: ["ISS-0261"]
title: "A release is offered features its platform cannot ship — the derived set is never filtered by `platform:`, so an Android release lists iOS work that no Android build can contain and that can never leave the list by shipping"
status: fixed
owner: user:edwin
created: 2026-08-30
updated: 2026-08-30
reviewed_by: model:claude-opus-5
review_date: 2026-08-30
review_verdict: changes-requested
severity: medium
component: tooling
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
fixed_in: "[[TASK-0587-The-Derived-Set-Is-This-Releases-Platforms]]"
source: ["Edwin, 2026-08-30, on ../your-trainer: 'The iOS features are un-released but they should not be added to this release, since this is an android only release.'"]
related: ["[[TASK-0587-The-Derived-Set-Is-This-Releases-Platforms]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[DES-0012-Tests-In-Two-Flows]]"]
---

# A release is offered work its platform cannot ship

## What happens

`shipping_in` returns `unreleased_payload` verbatim and `contents_candidates` uses its `platform` argument for exactly one thing — deciding what *another open release* has already claimed. Neither ever consults the **feature's** platform against the **release's**.

So on `../your-trainer`, `REL-0013` — `platform: android`, an Android-only patch — was offered nine iOS features plus `FEAT-0098` (iOS parity) as candidate contents, and listed them as held back on its page.

## Why it cannot resolve itself

A feature leaves the derived set by being named in a `released` release note. **`your-trainer` has no `ios/*` tag and no iOS release note**, because iOS has never shipped. So those ten had no exit: they were not merely wrong on one release page, they were structurally guaranteed to appear on every Android release prepared from then on.

That is the shape this matters in. A stale row that clears next cycle is noise; a row that cannot clear teaches people to stop reading the list.

## The cell the obvious fix gets wrong

*Include when the feature's platform equals the release's* is the one-line version, and it is a silent narrowing. Measured on `your-trainer` before writing the fix — 1,432 notes carrying `platform:`:

| value | notes |
|---|---|
| `android` | 818 |
| *(empty)* | 288 |
| `ios` | 284 |
| `cross` | 15 |
| `web` | 12 |
| `marketing` | 10 |
| `all` | 3 |
| `docs` / `both` | 1 each |
| **`shared`** | **0** |

`cockpit._platform_match` — the rule every nav mode uses — recognises `""`, `shared` and the picked value. **`shared` is a spelling this corpus never uses**, and equality would have dropped `cross`, `all`, `both` and every unset note from every release that named a platform: 303 of 1,432 by the empty column alone.

## Fix

`_ships_on` in `publication.py`, written as an **exclusion of a foreign platform** rather than a match: a feature leaves a release's contents only when it names a *different* platform. Unset, `cross`, `both`, `all` and anything unrecognised stay. Same conservative direction `ADR-0040` chose for check subtraction — selection may only ever remove what somebody can point at.

`unreleased_payload` is deliberately untouched. Those features **are** unreleased and the fleet card is right to say so; filtering there would hide genuinely unshipped work, which is the more expensive defect.

## The set had three readers, and fixing one fixed one

Found the way these are always found — by a person looking at the screen after being told it was fixed. Edwin, 2026-08-30: *"The left pane still doesn't show the correct info?"*

`shipping_in` and `release_payload` are the release **page**. The navigator's *Next release* group is built by `cockpit._publication_groups`, which read `unreleased_payload` **directly**, so scoping the page scoped the page: the left pane went on listing nine iOS features under an Android release, and from the reader's chair nothing had changed at all.

That is [[REQ-0059]]'s forbidden shape — one question, two implementations — and this computation has now supplied two instances of it. Both surfaces derive the set through `shipping_in`, and the guard is written as an **equality between them** rather than as a fact about either, so it fails whichever one moves next.

**A third reader is left alone deliberately.** `server.py`'s `create_release` stamps the unfiltered set into a new note's `features:`. It has no platform to filter by — `note_writes.create_release` takes no such argument and the note does not exist yet — and under the opt-in rule a release that has not said what it ships correctly takes everything. Narrowing it needs a platform on the way in, which is an API change and a decision rather than a fix.

## Still open, and not this issue's

`superseded` and `cancelled` satisfy `statuses.is_completed()`, so a replaced or abandoned feature is still offered as release contents — `your-trainer` has seven superseded iOS features and one cancelled. Excluding them changes what the fleet-wide Unreleased card counts in twelve repos, which is a decision rather than a fix, and it is filed separately.

## Independent review, 2026-08-30 — changes-requested

The predicate and its direction hold up, and the effect table reproduces exactly at the corpus state these commits were written against. Three findings against the issue as documented. [[ISS-0268]] — the scoping stops at the derived view: the navigator's `Nothing unshipped` placeholder now keys on the scoped set and can assert *"no features are waiting on a release"* while the Unreleased card lists two (constructed and run); `create_release` — disclosed here as safe — is the path by which the unfiltered set becomes the note's `features:` and comes back as `chosen` rows; and `mark_released` is a fourth reader whose frozen list moved silently. [[ISS-0266]] — the release page, which is the surface this issue is about, has no guard: reverting `release_payload`'s one changed line passes all 2126 tests. [[ISS-0270]] — `303 of 1,432` is neither the empty column (287) nor the set the sentence enumerates (306), and is measured over a population `_ships_on` never reads; and the `superseded`/`cancelled` follow-up this note says is *"filed separately"* does not exist.

Reviewed from a clean context (the notes and the diff, no authoring transcript) by `model:claude-opus-5`, the same model family as the author and a different session. Mutants were applied one at a time in a worktree at `c861414` and the full suite re-run; corpus figures were recomputed against `git archive fb99a751`, the `../your-trainer` state as of these commits.
