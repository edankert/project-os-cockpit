---
type: "[[task]]"
id: TASK-0378
aliases: ["TASK-0378"]
title: "~review, its mode and its button go, with the migration that stops a stored preference stranding the reader"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[FEAT-0090-The-Desk-Retires]]"]
parent: "[[FEAT-0090-The-Desk-Retires]]"
effort: M
due: ""
depends: ["[[TASK-0377-The-Registers-Re-Home]]", "[[FEAT-0071-Since-You-Looked]]"]
blocks: []
related: ["[[FEAT-0084-One-View-Vocabulary]]", "[[ISS-0063-Dead-Stat-Tiles]]"]
tests: ["[[TST-0022-Surface-Ownership]]"]
---

# The route retires

## Definition of Done
- [x] Every row of [[ADR-0020]]'s re-homing table is reachable at its new home — **walked** against the live corpus, item by item, and recorded below
- [~] `~review`, the `review` mode and its button are gone; a stored preference or deep link migrates — **the mode and the button are gone and migrate; the route stays served**, for the measured reason below
- [x] The overview's Tests stat tile navigates somewhere live — done in [[TASK-0371]], and now guarded by a test that renders the destination rather than naming it
- [~] `review_queue_payload` and the desk renderers are deleted, or the note records why they stay — **they stay; the reason is recorded**
- [x] The review ledger and its store are untouched — `/api/cockpit/review-queue` and `/api/cockpit/review-resolve` unchanged, asserted
- [x] A test asserts the badge total equals the registry total with no desk present — `test_the_badges_still_total_the_registry_with_no_desk`
- [x] [[TST-0022]]'s desk steps are rewritten, and it passes

## Steps
- [ ] Walk the re-homing table item by item and record the walk
- [ ] Retire the mode in both renderers via `RETIRED_NAV_MODES` — one view, one verdict, per [[FEAT-0084]]
- [ ] Re-point the Tests tile
- [ ] Delete the payload and renderers; keep `review.py`'s store

## Notes
**Retire in both front doors or neither.** Mode 1 has no Review button today, so this is mostly mode 3 — but the view set is the thing [[FEAT-0084]] is single-sourcing, and leaving a half-retired mode is how `recent` ended up with two verdicts.

[[ISS-0063]] is the stat-tile bug in its exact form: retiring a mode is how a live tile becomes a dead click, and the Tests tile points at `~review` today.

The badge-equals-registry assertion is the one that makes removal provable rather than asserted — it is the whole reason this task comes last.

## Why this waits on FEAT-0071

[[ADR-0020]] accepts that removing the desk costs up to four visits where there was one, and names [[DES-0008]]'s landing digest as the mitigation. That digest is [[FEAT-0071]] in [[PHASE-026]].

Removing the desk first would ship the cost and not the mitigation — turning a trade-off the decision accepted into a regression it did not. The dependency is here rather than in prose so the ordering cannot lose it.

## Done 2026-08-10

### The walk

Nine rows of [[ADR-0020]]'s table, against this corpus rather than by inspection:

| desk element | new home | walked |
|---|---|---|
| Decisions — ADR `proposed` | Design | `ADR-0010`, marked owed |
| Proposals — requirement `draft` | Features | `REQ-0029..0032`, marked owed |
| Proposals — design `proposed` / offered | Design | **empty here** — no design has ever been `proposed`; the view owns the kind |
| Test runs — manual `ready`, and the stepper | Tests | **empty here** — all 23 tests pass; `~tests/<TST>/run` exists and the note carries `Run ▸` |
| Tests register | Tests | 23 rows plus the tier groups |
| `changes-requested` re-review | the view owning each note's type | 104 verdicts, **0 owed** — [[ISS-0121]]'s finding |
| "am I done" count | badges on the view buttons | `overview 81 · issues 7 · features 4 · intent 3 · tests 0` |
| Reviewed register | the record surfaces | [[TASK-0377]] |
| Questions | nowhere, deliberately | no obligation kind claims them — asserted |

Two rows are **empty in this corpus**, and that is exactly how `change` and `release` went missing from the registry ([[ISS-0128]]) — so they are asserted by their *view owning the kind*, not by having rows today.

### The route stays, and the reason is a measurement

The DoD says the route goes. **`.cockpit/review-requests.json` holds one OPEN entry.** Retiring `~review` today would strand it: an entry a human is expected to act on, with no surface anywhere.

The ledger is runtime state agents still write — proposals, questions, offered designs ([[ADR-0007]]: pending-ness is runtime state, not note state) — and where those flows finally land is **[[ISS-0126]]**, which is Edwin's decision and one of the four this release says to raise and stop on rather than guess at.

So: **the mode and the button are gone** and a stored preference migrates to `overview`; the route stays served; and the record column's `Reviewed` card carries a link to it **only when the ledger has an open entry**. That keeps the one live request reachable without leaving a door to an empty room — and when ISS-0126 is answered, deleting the route is a small change with nothing behind it.

`review_queue_payload` and the desk renderers stay for the same reason and no other. They are reachable from that link and from nowhere else.

### One thing the retirement nearly broke

`MODES_WITH_VIRTUAL_LANDING` still listed `review`. That set decides what the centre pane does on workspace open, so a mode with no button claiming a landing would have sent the reader to a page they did not ask for and could not navigate away from by clicking. Caught by `test_the_boot_path_does_not_race_a_virtual_landing_mode`, which asserts the set exactly — one of the few tests in this repo that is stricter than it looks.

### Verification

`927 passed, 2 skipped`; `validate-docs: OK`; `tsc --noEmit` clean; `dist/` rebuilt. Adequacy by mutation:

| mutation | killed by |
|---|---|
| show the ledger link when the ledger is empty | `test_the_review_route_stays_while_the_ledger_has_open_entries` |
| drop `review`'s migration fallback | `test_the_desk_button_and_mode_are_gone_and_migrate` |
| take `change`'s owning view away | `test_the_badges_still_total_the_registry_with_no_desk` + 1 |
