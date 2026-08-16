---
type: "[[issue]]"
id: ISS-0182
aliases: ["ISS-0182"]
title: "The tests assert counts and kinds and never the content, the order or the address — every bug Edwin reported personally shipped without a regression test, and three of them can be reintroduced with the full suite green"
status: "open"
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-16
updated: 2026-08-16
source: ["Independent mutation audit of PHASE-034, 2026-08-16; load-bearing claims re-verified by execution"]
severity: high
component: cockpit-server
parent: ""
related: ["[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]", "[[ISS-0179-Six-From-Reading-The-Release-View]]", "[[ISS-0180-The-Release-Page-Printed-What-It-Should-Have-Rendered]]"]
tests: []
---

# The tests assert counts and kinds, never content, order or address

An independent mutation audit ran the full suite against deliberate breakages. Seven survived. The pattern is one sentence, and it is the same shape as the phase's central failure — *criteria that can be satisfied without the reader being helped.*

## Verified by execution

| mutation | result |
| --- | --- |
| Invert the release ordering — **the exact bug [[ISS-0179]] reported** | **1400 passed** |
| `acceptance.locate` always returns the first checkbox line | green — the only fixture rewrites `1.1.1`, which *is* the first |
| Delete the name guard in `rewrite_check` entirely | green — its test passes the correct name, so the guard never fires |
| Empty `contents["ids"]` **and** `contents["rows"]` on the shipped branch | green — `ids` is asserted nowhere in the repo |
| `shipped = held is not None` | green — **a release mid-preparation would take the frozen path and silently lose its gate** |

## Blocking: a ticked criterion cites a test that does not exist

[[FEAT-0103]]:61, ticked, on a `done` feature, cites `test_editing_a_row_above_does_not_move_the_target` as its evidence. That test appears **nowhere in `tests/`** — it was retired with the walker in [[FEAT-0107]] and the tick was left standing. Verified: the only occurrences in the repo are that criterion and [[TST-0029]]'s note.

## Two structural gaps

**The release page has no test of any kind.** `renderReleasePage`, `buildReleasePage` and the `~release` route: zero hits in `tests/`. The generic nav-url sweep accepts any `~whatever` whether a handler exists or not.

**`preparing` never reaches `release_payload` in any test.** All 14 call sites pass `next` with no note, or a `released` one. The file that builds `preparing` fixtures never calls the payload. So the state its own docstring calls *"the whole design"* is never rendered in a test.

## And the dead code is the safe path

`acceptance.locate` / `rewrite_check` are the **correct** addressing mechanism, have zero callers in `src/`, and `TASK-0442` justifies keeping them because they are *"covered by `test_acceptance_exceptions.py`"* — coverage that exercises neither property that matters. So the safe path is untested and unused while the unsafe one ([[ISS-0177]]) is live.

## Expected

Regression tests for the three defects Edwin reported personally, since all three shipped without one; a fixture with more than one release, because ordering is unobservable with one; a `preparing` release reaching the payload; and any test at all for the release page.
