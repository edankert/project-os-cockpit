---
type: "[[requirement]]"
id: REQ-0014
aliases: ["REQ-0014"]
title: "Cockpit platform filter — auto-discovered, picker only when used"
status: verified
implements: ["[[FEAT-0006]]"]
phase: "[[PHASE-002-Project-OS-Adapter]]"
owner: user:edwin
created: 2026-05-08
updated: 2026-05-23
source: []
priority: medium
scope: "FEAT-0006"
specifies: ["[[FEAT-0006]]"]
verifies: []
related: ["[[REQ-0013]]", "[[TASK-0017]]"]
tests: ["[[TST-0002]]"]
---

# REQ-0014 — Cockpit platform filter

## Statement
The cockpit SHALL support filtering both panes by `platform` for multi-platform projects (iOS, Android, web, …). The filter SHALL be **auto-discovered** from the docs corpus — projects that don't tag any note with `platform` MUST NOT see the picker UI at all.

### Auto-discovery
The `/api/cockpit/nav` payload SHALL carry an `available_platforms` field: a sorted list of distinct non-empty `platform` frontmatter values found across all real notes (templates excluded, empty/missing values not listed). The JS client SHALL render the picker if and only if this list is non-empty.

### Picker UI
A pill toggle group in the page header, between the breadcrumb and the "Hide completed" filter. One pill per discovered platform, plus a leading "All" pill (default). The picker SHALL be data-driven from `available_platforms` — adding a new value (e.g. `web`) anywhere in the corpus causes a "Web" pill to appear automatically with no code change. Display labels SHALL be title-cased per pill, with explicit overrides for `iOS` and `Android` to preserve canonical capitalisation.

### Filter semantics
For a selected platform `P`:

- include records whose own `platform` is `P`, `shared`, or empty/missing
- otherwise drop the record

So a phase note with no `platform` always passes (cross-cutting), a `shared` task always passes (cross-platform by design), and a `platform: ios` record only shows under iOS or All. Picking a value not present in any record (e.g. `web` on a project that only tags ios/android) effectively narrows to cross-platform notes.

The "All" pill disables the filter entirely.

### Scope
The filter SHALL apply to:

- the **left pane** in every mode (Features / Tasks / Issues / Recent)
- the **right pane** (linked + inbound-only relationships of the active note)

The filter SHALL NOT apply to:

- the **centre pane** content (the active note's body — that's a single note, not a list)
- the auto-index pages (`/index/<plural>`) — those predate the cockpit and stay platform-agnostic

### Persistence + safety
Selection SHALL persist in `localStorage` under `project-os-cockpit.cockpit.platform`. Default `all`. If a saved selection points at a platform value that no longer exists in `available_platforms` (e.g. the field was removed from the project), the JS client SHALL silently fall back to `all` rather than render an inert pill.

### Query parameters
The API SHALL accept `?platform=<value>` on both `/api/cockpit/nav` and `/api/cockpit/context`. Missing or `all` means no filter. Unknown values are passed through and used as the filter target — yielding the cross-platform-only narrowing described above.

## Acceptance Criteria
- Pointed at a docs tree where no note has a `platform` value (this repo's own `docs/`), the cockpit header renders without a platform picker. `available_platforms` is `[]`.
- Pointed at `../your-trainer/docs/`, the picker shows three pills: `All / iOS / Android`. Toggle behaviour:
  - `iOS` → left pane shows iOS-tagged + shared + agnostic items; Android-tagged items are absent.
  - `Android` → mirror.
  - `All` → no filter.
- Right-pane relationships of the active note are filtered by the same predicate. An Android-tagged task targeting an active feature does not appear in the linked list when iOS is selected.
- Selection persists across page reloads.
- Manually setting `localStorage.platform` to `web` (a value not in the corpus) renders no picker pill highlighted — UI silently treats the selection as `all`.
- Adding a third platform value (e.g. `web`) to a single note in the docs tree causes a "Web" pill to appear on the next nav refresh, without editing the JS or CSS.

## Rationale
project-os schemas allow `platform` as an optional string (`ios | android | shared | ""`). For multi-platform mobile projects (`your-trainer`), browsing iOS-relevant work separately from Android-relevant work is a daily activity — without a filter the cockpit lists are dominated by the platform you're not currently working on. For single-platform or non-mobile projects, the field is unused, so the picker would just be visual clutter; making it auto-discover keeps the UI honest.

`shared` and platform-agnostic notes (phases, ADRs, project-level requirements) intentionally always pass the filter — the user wants iOS context **plus** the cross-cutting state, not just iOS-tagged items.

The picker is data-driven (rather than a hardcoded "iOS / Android" pair) so the same code works for any platform taxonomy a project might adopt — `web`, `desktop`, `tv`, etc. — without per-project changes to project-os-cockpit.

## Traceability
- Implements: [[FEAT-0006]]
- Related: [[REQ-0013]] (cockpit layout — header controls section)
- Implemented by: [[TASK-0017]]
- Verified by: [[TST-0002]] — test cases `test_nav_payload_surfaces_available_platforms`, `test_nav_payload_platform_ios_filters_tasks`, `test_nav_payload_platform_unknown_falls_back_to_all`, `test_context_payload_platform_filters_relationships`, `test_context_payload_platform_drops_other_platform`.

## Verification
- 2026-05-23: marked `verified` — Platform filter shipped (TASK-0017, CHG-20260508-Cockpit-Platform-Filter).
