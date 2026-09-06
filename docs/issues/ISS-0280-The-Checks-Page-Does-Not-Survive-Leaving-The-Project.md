---
type: "[[issue]]"
id: ISS-0280
aliases: ["ISS-0280"]
title: "Leaving a project and coming back lands on the Tests landing instead of the filtered checks list — the page and the tier/area filters live in module state that nothing persists per workspace"
status: fixed
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-06
updated: 2026-09-06
source: ["Edwin, 2026-09-06, after walking v2.1.x's suite in ../your-trainer"]
severity: medium
component: ui
parent: ""
related: ["[[SUR-0001-The-Tests-View]]", "[[ISS-0263-A-Write-Evicts-The-Reader-From-The-Checks-Page]]", "[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[ISS-0193-The-Tests-Landing-Overwrites-The-Checks-Page]]", "[[ISS-0203-Tier-Selection-Does-Not-Change-The-Page]]", "[[REQ-0042-The-Suite-Is-Addressable]]", "[[ISS-0281-A-Failing-Verdict-Is-Erased-From-The-Checks-View]]"]
tests: []
---

# The checks page does not survive leaving the project

## Problem

A reader walking a filtered set of checks switches to another project and comes back. The cockpit shows the Tests landing (`~tests`), not the checks list, and the tier and area filters are gone. The walk has to be set up again from the start.

> [!quote] As reported — 2026-09-06 (user:edwin)
> When moving away from the project the selected acceptance tests are no longer visible when going back

## Repro

1. Open `../your-trainer` in the shell. Tests view, `~checks/tier/1`, then pick an area in the filter bar.
2. Switch to any other workspace in the sidebar.
3. Switch back to your-trainer.

## Expected

The same page with the same tier and area filters, scrolled to where the reader left it or close to it.

## Actual

The Tests landing (`~tests`). Opening `~checks` again shows the whole suite with no filter.

## Cause (diagnosed by the main session, 2026-09-06)

Two losses on one switch, and nothing stores either per workspace.

1. **The page.** `currentNavMode` is stored globally (`localStorage` key `cockpit:nav-mode`), but the page is not. `openWorkspace` clears `currentRel`. On `sidecar:ready`, `loadWsNav()` lands the Tests view on `~tests` because `tests` is in `MODES_WITH_VIRTUAL_LANDING` (`desktop/src/renderer/renderer.ts:4067`).
2. **The filters.** `checkFilters` is module state with no persistence. `renderChecksPage` clears the tier and area axes on every address-driven render, which is [[ISS-0262]]'s `keepFilters` rule working as designed.

Pinned docs (`cockpit:pinned:<workspaceId>`) and the platform picker already persist per workspace. The page a reader was on does not.

## Impact analysis: the fix must not undo ISS-0203

[[ISS-0203]] and [[ISS-0262]]'s third guard say the address wins on navigation: arriving at a bare `~checks` must not inherit a previous filter. Persisting `checkFilters` itself and restoring it on arrival would break that rule.

The reading that keeps both: persist the **address** per workspace (`~checks/tier/1`, `~checks/area/<area>`, [[REQ-0042]] made them addressable for this reason) and restore it as the page to return to, instead of landing on `~tests`. The filters then come back through the address, and a bare `~checks` still resets. No conflict once the fix is address-shaped; a filter-state fix would conflict.

Assumption to record in the fix: the last page is restored per workspace for the Tests view. Whether the same should hold for every view's last page is a wider change and is not this issue.

### What shipped: the address AND the filters, on a third case

The address alone does not carry the walk. Two of the five filter axes fit in an address — `~checks/tier/1`, `~checks/area/<area>` — and three do not: **mark**, **covers** and **automation** have no route, and `mark` is the axis a walker actually uses, because filtering to what is still owed is how a 624-row suite is worked through in sittings. Restoring only the address would have brought the page back and left Edwin re-selecting the filter that made it a walk.

Both are stored, under `cockpit:checks-place:<workspaceId>`, and [[ISS-0262]]'s rule is untouched. That rule is about what an *address-driven render* does with axes the address does not name, and it still clears them. The restore is a **third case** beside navigation and repaint: the shell puts the reader back where they were, so it hands the render the filters to apply through `pendingChecksFilters`, which is consumed by exactly one render. A navigation after that clears as before, and `test_a_restore_is_neither_a_navigation_nor_a_repaint` asserts both halves.

## Sibling search

Siblings exist, and this is the fourth issue of its kind on this page: [[ISS-0193]] (the Tests landing painted over `~checks` on a view switch), [[ISS-0262]] (a mark cleared the filters), [[ISS-0263]] (a note write evicted the reader to the landing). Each was fixed at its own trigger: view switch, write, watcher refresh. This one is the workspace switch. Per `tools/skills/issue-intake/SKILL.md` step 2, the second sibling is the harvest trigger, and this family is past it. A rule-ADR is proposed rather than written: *a page a person walks step by step keeps its address and its filters across every event that repaints it, and the events are enumerated (view switch, write, watcher refresh, workspace switch, reload).* Edwin's call whether to mint it; the fix here does not wait on it.

## Risk scan

No trigger applies. One more `localStorage` key per workspace, in the pattern `cockpit:pinned:<workspaceId>` already uses; no dependency, env var, path or contract.

## Next Actions

- [x] Persist the Tests view's last address per workspace and restore it on `sidecar:ready` instead of landing on `~tests`.
- [x] Guard: a test that stores `~checks/tier/1` for a workspace, simulates the return, and asserts the address restored is that one and that a bare `~checks` still clears the axes (the ISS-0203 rule).
- [x] Update `docs/reference/cockpit-capability-register.md` in the change-note commit (the shell gains capability: a workspace remembers its checks page).
