---
type: "[[issue]]"
id: ISS-0169
aliases: ["ISS-0169"]
title: "The deploy half of the publication obligation can stop counting with the whole suite green — finding 3's sibling kind, on the box that was ticked without evidence"
status: fixed
phase: ""
owner: user:edwin
created: 2026-08-15
updated: "2026-08-15"
source: ["Independent review of [[FEAT-0100]] returning to `done`, 2026-08-15: the close-out's own instruction was to verify finding 3 by mutation and then look for other vacuity in the same area."]
severity: medium
component: obligations
parent: ""
related: ["[[FEAT-0100-Unpushed-Work-Needs-A-Person]]", "[[TASK-0417-Publication-Enters-The-Registry]]", "[[ADR-0027-The-Registry-Counts-What-Needs-A-Person]]", "[[PHASE-030-Obligations-Go-Home]]"]
tests: []
---

# The deploy publication obligation is guarded by nothing

## What was checked, and what it found

[[FEAT-0100]]'s close-out closes independent-review finding 3 — *"no test exercises the publication source non-vacuously"* — with `test_the_publication_obligation_is_exercised_non_vacuously` in `tests/test_view_landings.py:1004`. **That claim is true and reproduces.** Mutating `_publication_rows` (`src/project_os_cockpit/obligations.py:336`) to `return []` fails it:

```
FAILED tests/test_view_landings.py::test_the_publication_obligation_is_exercised_non_vacuously
FAILED tests/test_history_payload.py::test_an_unknown_publication_count_is_not_reported_as_zero
2 failed, 1284 passed
```

The new test covers **one** of the two publication kinds. `PUSH_OBLIGATION_KIND` (`unpushed commit`, verb `Push`, `remote_kind="backup"`) is now asserted end to end. `DEPLOY_OBLIGATION_KIND` (`undeployed commit`, verb `Deploy`, `remote_kind="deploy"`, `obligations.py:403`) is asserted by nothing.

**Reproduction.** Replace the deploy source's row builder so the kind never yields:

```python
NOTE_LESS[DEPLOY_OBLIGATION_KIND] = NoteLessObligation(
    kind=DEPLOY_OBLIGATION_KIND,
    view=VIEW_OVERVIEW,
    verb="Deploy",
    rows=lambda index: [],            # was _publication_rows(..., "deploy")
```

`.venv/bin/pytest -q` → **1286 passed, 2 skipped**. A whole obligation kind stops being counted on the badge, in `Needs you` and on the landing page, and nothing in the repo notices. `grep -rni deploy tests/ desktop/tests/` returns remote *classification* tests (`remote_kind`) and the fleet-side `ahead` count, and nothing that asserts the **registry** counts this kind.

## Why this is the same defect and not a smaller one

It is the kind that matters most on the fleet. The independent review of 2026-08-14 recorded the live numbers itself: `your-applications.com` at **34** commits on a deploy remote (`production/master`, `root@76.13.51.7:…`). A repo whose only remote is a deploy target has *every* one of its unpublished commits counted under this kind and none under the other, so this is the whole publication badge for that project.

[[TASK-0417]]'s Definition of Done carries a box for exactly it:

> - [x] **A deploy remote is counted, under its own kind** — `commits to deploy`, distinct from `commits to push`… The breakdown reads both separately, the total includes both, and the deploy row **names** its action without offering it

That box was ticked at close-out on 2026-08-14 and is **the only one of the six with no evidence appended**; the other five each carry a named test or a named symbol. [[FEAT-0100]] line 124 states *"26 ticked with evidence"*. This is one of seven ticked boxes across the three tasks that carry none.

## Suggested fix

Extend `test_the_publication_obligation_is_exercised_non_vacuously`, or add a sibling, that points the fixture repo's `origin` at a deploy-shaped URL (`root@host:/srv/x.git`, which `remote_kind` already classifies) and asserts `counts_by_kind(...)["overview"]["undeployed commit"] == 2`, `len(rows) == 2`, and `verb == "Deploy"`. The fixture in `tests/test_view_landings.py:1020` already builds a bare repo and rewrites the remote with `pushInsteadOf`; the deploy case is cheaper, because it never needs to push.

The `names but does not offer` half is separately covered by `test_the_push_has_exactly_one_implementation` on the renderer side; what is missing is only that the count exists at all.

## Fixed — 2026-08-15

`test_the_deploy_publication_obligation_is_exercised_non_vacuously` in `tests/test_view_landings.py`. It builds a repo whose only remote is a bare filesystem path — which `remote_kind` classifies `deploy` by its own rule that anything unrecognised is a deployment target — commits three times without pushing, and asserts `counts_by_kind` reports `undeployed commit: 3`, that `owed_items` yields exactly three rows carrying the verb `Deploy`, and that the landing payload agrees on both.

It also asserts `unpushed commit` is **absent**, because the failure worth catching is not only "stops counting" but "counts under the wrong kind" — the two collapsing would silently destroy the distinction the deploy refusal exists to make.

**Verified against the exact mutation this issue reports**: replacing the deploy source's `rows` with `lambda index: []` now fails this test, where before it left 1286 passing.

The sibling test for `unpushed commit` was written a day earlier for finding 3 and did not generalise, which is the whole lesson here — the fixture it needed was a *different remote kind*, so copying the shape was not enough and neither was noticing that finding 3 had a sibling.
