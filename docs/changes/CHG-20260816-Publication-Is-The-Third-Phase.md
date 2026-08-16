---
type: "[[change]]"
id: CHG-20260816
title: "Publication becomes the third phase and gets a view, and an obligation asks only while its subject is in flight — your-trainer's owed count goes 64 to 31"
status: merged
owner: user:edwin
created: 2026-08-16
updated: "2026-08-16"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
source: ["Edwin 2026-08-16, from use of ../your-trainer"]
related: ["[[ADR-0028-Work-Has-Three-Phases]]", "[[FEAT-0101-Obligations-Route-By-The-State-Of-Their-Subject]]", "[[FEAT-0102-Publication-Becomes-A-View]]", "[[ISS-0172-A-Manual-Test-With-Subsections-Has-No-Runnable-Steps]]", "[[ISS-0173-The-Suites-Own-Ids-Are-Written-In-A-Form-Nothing-Reads]]", "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"]
tags: [obligations, publication, surfaces]
---

# Publication is the third phase

## What changed

**A ninth nav mode, `publication`.** The eight existing modes are untouched — nothing renamed, merged or removed, and no note changes address. It holds the whole ladder: what is uncommitted, what is unpushed, what is undeployed (named, never offered), and the releases and tags. `~history` still resolves.

**Obligations route by the state of their subject.** A requirement or a manual test asks while a feature it names is being worked, and rests otherwise. `deferred` still overrides. Nothing changes for issues at `triage`, which are owed in every phase.

**Two publication obligations moved off `overview`** — a view that is not a nav mode, so their rows reached no navigator and had to be hand-carried to the attention panel. They live on `publication` now.

**The acceptance suite's release gate reaches a surface for the first time.** One obligation while a release is `draft`, zero otherwise, and the number is stated rather than summed.

## What a person will notice

| | before | after |
| --- | --- | --- |
| `your-trainer` owed | 64 | **31** |
| — requirements to approve | 26 | 3 |
| — manual tests to run | 15 | 5 |
| — issues to triage | 22 | 22 |
| unrunnable manual tests (fleet) | 8 in one repo | **0 in twelve** |
| pages stating the release-gate number | **none** | the Publication view |

Nothing was hidden: the 33 items the rule quieted render as a collapsed `Quiet · N` line under Features and a `Resting · no feature in flight` group under Tests, each row naming its subject and that subject's status.

## Paths and contracts

- **New:** `src/project_os_cockpit/publication.py`; nav mode `publication`; `obligations.VIEW_PUBLICATION`; `obligations.suppressed_items()`; `cockpit.suppressed_group()`; `acceptance.heading_refs()`.
- **Moved:** `unpushed commit` / `undeployed commit` obligations from view `overview` to `publication`. A caller reading `owed_items(index)["overview"]` for these gets an empty list.
- **Changed signature:** `cockpit._owed_flag(record)` → `_owed_flag(record, index)`. Without the index it cannot apply the in-flight rule and marks rows the badge does not count.
- **Derived, not walked:** `obligations.counts_by_kind` now comes from `owed_items` rather than a second pass.
- **Fixed:** the acceptance suite's group url was `/tests/…`, which `extractRel` drops — a dead click since TASK-0373. Now `/docs/tests/…`.

No write path widened. `REQ-0026`/`REQ-0027` still gate every mutating route, pushing is still a person's click, and deploying is still named and refused.

## Verification

Full suite **1351 passed, 2 skipped**. Four new `TST-*` notes at `passing`, 47 new assertions across three files plus nine in `test_review_desk.py`. Twenty mutations run against the new guards, each chosen to defeat rather than confirm; one no-op from bad shell escaping was caught by an apply-check and re-run before being believed, and one survivor was characterised as an equivalent mutant rather than counted as a pass.

Walked against a live sidecar on `your-trainer`, and the ladder walked across all twelve discovered repos.
