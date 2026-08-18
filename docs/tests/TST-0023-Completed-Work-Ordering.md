---
type: "[[test]]"
id: TST-0023
aliases: ["TST-0023"]
title: "Completed work orders rather than disappears — both surfaces, checked by mutation"
status: passing
covers: ["[[FEAT-0056-Completed-Work-Ordering]]", "[[FEAT-0057-The-Record-Grammar]]", "[[FEAT-0058-One-Shape-Per-Navigator]]"]
command: ".venv/bin/pytest tests/test_completed_work_ordering.py -q"
phase: "[[PHASE-022-Completed-Work-Gets-Quieter]]"
owner: user:edwin
created: 2026-08-02
updated: 2026-08-13
source: ["[[FEAT-0056-Completed-Work-Ordering]]"]
scope: "system"
level: "unit"
entrypoint: "tests/test_completed_work_ordering.py"
artifacts: []
evidence: ["30 passed in 0.75s (2026-08-02); desktop node suite 65 passed"]
last_run: "2026-08-13T18:28Z"
related: ["[[TASK-0267-One-Comparator-Open-Before-Done]]", "[[TASK-0268-Groups-With-Open-Work-Sort-First]]", "[[TASK-0269-The-Context-Pane-Stops-Filtering]]", "[[TASK-0270-Folding-Keyed-On-Length]]"]
last_verified: 2026-08-02
exit_code: 0

---

# Completed work ordering

## What it covers

`tests/test_completed_work_ordering.py` (30 cases) plus the FEAT-0056 block in `desktop/tests/fleet-health.test.mjs` (15 cases, run from pytest by `test_desktop_node_suite.py`).

- the comparator, **and its call sites** — the two are separate assertions on purpose
- phase group banding: in flight / upcoming / finished
- the context pane never filtering by state — asserted through `contextGroupRows`, which takes **no** collapse parameter, so reintroducing the filter means editing that function rather than a call site
- the fold's `head + hidden == items.length` invariant, at every limit including 0 and negative
- ISS-0082: dangling phase links, and a retitled phase not forking its group
- **mode 1's hand-written twin**, executed through node and checked against mode 3's answers

## Why it is shaped this way

The first version of this suite passed while the behaviour was broken. Independent review ran mutations and found five guards that could not fail:

| mutation | first suite | now |
|---|---|---|
| delete the open-first sort in `_open_first` | **green** | fails |
| delete it in `_features_groups` | **green** | fails |
| delete `_settled_last` from the issue buckets | **green** | fails |
| re-introduce ISS-0082's stale link | **green** | fails |
| anything at all in `static/cockpit.js` | **green** — no guard existed | fails |

Round 2 then found three more that round 1's rework had not covered:

| mutation | after round 1 | now |
|---|---|---|
| make the context pane filter by state (one character) | **green** | fails |
| delete `foldGroup`'s limit hardening | **green** | fails |
| delete `foldGroup`'s null tolerance | **green** | fails |

A final sweep of twelve mutations across all three sources then found one more survivor: mode 3's `contextGroupRows` was covered by the node suite while **mode 1's twin was not**, so flipping its one `false` to `true` left everything green — the same surface, caught for the same class of gap, twice.

The first of those is the feature's headline change. It had no guard on either surface for a full round — which is why `contextGroupRows` exists at all: a function whose signature cannot express the mutation is a stronger guard than a test that has to remember to look for it.

Two of those could not be caught by this repo's own corpus: its feature IDs already happen to run open-first, and it has **zero** open issues, so both sorts are no-ops on it. Those cases now build a fixture corpus in which ID order and open-first order deliberately **disagree**.

A guard that only fails on data we happen to have is a guard that expires. Two exit criteria in [[PHASE-022]] expired exactly that way — "PHASE-022 sorts 1st" and "ISS-0082 leads the Medium bucket" both stopped being true the moment the work closed.

## Evidence

`pytest tests/test_completed_work_ordering.py` → 30 passed. `node --test desktop/tests/*.test.mjs` → 65 passed. Twenty mutations were run by round-1 review against the rebuilt suite and all twenty fail; round 2 then found three more the suite could not catch (the context pane's filter, and both halves of `foldGroup`'s input hardening), and those are guarded now too.
