---
type: "[[change]]"
id: CHG-20260811-P026
title: "PHASE-026 closes — done-but-unshipped is a number, drafting a release is an action, every empty state speaks, and Caught up finally moves the watermark"
status: merged
date: 2026-08-11
owner: user:edwin
related: ["[[PHASE-026-The-Returning-Human]]", "[[FEAT-0072-The-Release-Surface]]", "[[FEAT-0073-One-Voice]]", "[[ISS-0134]]", "[[RISK-0005]]", "[[ADR-0021]]", "[[REL-0001-The-Human-Has-Levers]]"]
tags: [change]
---

# PHASE-026 closes

The first of [[REL-0001]]'s five phases to reach `done`. Taken first deliberately: the release surface is what stops REL-0001 being hand-maintained, and that note had already drifted once ([[FEAT-0078]] missing from its own deferred table).

## What shipped

**[[FEAT-0072]] — the release surface.**

- `Unreleased · 70` on the overview's record column. Membership decides it, not dates: a feature is shipped when a `[[release]]` note names it, and **only a `released` one ships anything**. Today that is the whole story — REL-0001 is `draft`, so the card reads *"70 features done, none in a shipped release yet"* rather than naming a release that has not happened.
- `Draft release note` — allocates an id, writes one file, `status: draft`, `date: ""`. It publishes nothing. `CREATABLE_TYPES` widened from `{issue}` to `{issue, release}` with the review the rule demands recorded on the constant.

**[[FEAT-0073]] — one voice.**

- Nine empty states rewritten to say what the pane shows *and* the shortest path to having some. The three that named nothing at all — `(no items)`, `(no children)`, `All clear.` — are gone.
- The collapse-completed eye is **defended rather than retired**: it folds the completed tail of *mixed* groups, which the per-card default cannot do, so they are two mechanisms for two ideas rather than one.
- [[DES-0002]] gains a `Deliberate exceptions` section: obligations-not-collections, files-not-lifecycle-notes.
- [[ADR-0021]], `proposed` — mode 1 stays and stops being hand-written.

**[[ISS-0134]] — `Caught up` works.** Reported by Edwin after clicking it three times with nothing happening.

**[[RISK-0005]] — closed.** Its own closing condition was a suite that enumerates the route table; that exists and covers 21 POST routes, and REL-0001's pass drove 10 of 10 mutation endpoints over a real LAN interface for 403s.

## The one worth reading twice

`computed_at` was the newest commit's **day**. Every commit was also a day. So on any day somebody was working, catching up wrote today's date and today's commits still ordered as "not before" it — the watermark could not advance *within* a day, which is exactly when a person clicks the button.

Git had been handing the full `%aI` instant to `history_payload`, which truncated it at `when[:10]` and threw it away. Commits now carry `ts` beside `date`, and the comparison orders exact instants when both sides have them.

Two things this exposed:

- **The needs-you half is not filtered by the watermark, and must not be.** An obligation is discharged by acting on it, not by reading it. That half was correct and the *presentation* was lying: the button sat under both halves and clicking removed the whole band. It now says *"These stay until they are discharged — Caught up covers what changed, not what is owed."*
- **Removing `band.remove()` was not enough.** `refreshDigests` updates the rail's cache and never touches the band, so the first fix traded a false dismissal for stale content — measured at `12 transitions` still on screen four seconds after the click. The handler now re-mounts explicitly.

## Verification

Full suite green. New: `tests/test_unreleased.py` (10), `tests/test_digest_watermark.py` (6), `tests/test_empty_state_voice.py` (4).

Two tests were **generalised rather than deleted** when correct behaviour broke them:

- `test_a_proposed_adr_is_this_views_obligation` pinned the owed set to `{"ADR-0010"}` and failed when ADR-0021 was proposed. It now asserts the *property* — every `proposed` ADR is owed — so the next proposal does not break it.
- `test_the_creatable_type_allow_list_is_one_type` became `..._is_reviewed_not_open`, still an exact-set assertion so the next widening is visible.

The `unreleased` shipped-release branch is tested against a **built** `released` note, because no release in this corpus has ever been `released` and that branch does not run here. It was broken when first written — a `NameError` on an unimported helper — and every test against the live corpus stayed green.
