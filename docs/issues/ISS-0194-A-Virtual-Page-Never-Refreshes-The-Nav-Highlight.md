---
type: "[[issue]]"
id: ISS-0194
aliases: ["ISS-0194"]
title: "No virtual page refreshes the nav highlight, so the left pane goes on pointing at the note you left — `~checks`, `~sweep`, `~history`, `~accept` and the test runner all inherit it"
status: fixed
owner: user:edwin
created: 2026-08-18
updated: "2026-08-18"
severity: medium
component: desktop-renderer
phase: "[[PHASE-035-Acceptance-Checks-Are-Notes]]"
related: ["[[FEAT-0114-The-Suite-Is-A-View]]", "[[ISS-0193-The-Tests-Landing-Overwrites-The-Checks-Page]]", "[[ISS-0132-A-Phase-Cannot-Be-Opened-From-The-Navigator-That-Groups-By-It]]"]
---

# A virtual page never refreshes the nav highlight

## What happens

Open the acceptance checks from **inside** the Tests view — the `Tier 1 — feature tests · 306/347` group head — and the checks page renders correctly. The left pane goes on highlighting whichever note you were reading before.

The pane does not show *no* selection. It shows the **wrong** one, confidently.

## Why

`refreshActiveNavRow()` has exactly two call sites: `renderDoc` (`desktop/src/renderer/renderer.ts:1571`) and `renderWsNav` (`renderer.ts:11107`). Every virtual-page branch in `navigateTo` repeats the same four lines —

```ts
currentRel = normalised;
currentDispatchHistory = null;
currentNoteStatus = null;
pushHistory(normalised, opts.replace ?? false);
refreshFooterPath();
```

— and **none of them calls it**. `~checks` (`renderer.ts:1284`), `~sweep/<FEAT>` (`:1272`), `~history` (`:1294`), `~accept/<FEAT>` (`:1326`), `~tests/<TST>/run` (`:1339`), `~review`, `~design`, the view landings (`:1397`). The duplication is the cause: the block was copied seven times and one line of it was not in the copy.

The tier heads already carry the address — `summary.dataset.rel = groupRel` at `renderer.ts:11753`, and `extractRel` passes `~checks` through (`:11884`). Nothing needs to change in the payload or the DOM. The sweep just never runs.

## Why it looks intermittent

Edwin: *"**Sometimes** … the acceptance tests are not selected."* Anything that reloads the navigator calls `renderWsNav`, which does call the sweep — so the highlight appears when, and only when, something else happens to repaint the pane:

- a mode switch (`setNavMode` → `loadWsNav`), which is why arriving from Publication looks different from arriving from Tests — and lands you somewhere else entirely ([[ISS-0193]]);
- the file-watcher soft reload (`renderer.ts:13293`), which fires whenever a file changes under you.

So the same click highlights or does not depending on whether a watcher happened to tick. That is the "sometimes", and it is why this reads as flaky rather than as absent.

## Expected

Navigating to any address — note or virtual page — leaves the left pane highlighting that address, or nothing. Never the previous one.

## Scope

The Electron renderer. The browser front door has the mirror-image defect and it is **not** this issue: `cockpit.js:2029` matches on `a.getAttribute("href") === active.url`, and group heads render as `.group-header-link`, which the `.nav-item` sweep does not see. Worth checking under [[PHASE-029-One-Tool-Two-Front-Doors]] (one tool, two front doors) rather than patching here.

## Next actions

- [ ] Hoist the repeated five lines into one helper that also calls `refreshActiveNavRow()`, so a virtual page added tomorrow inherits the highlight rather than the omission.
- [ ] A guard that navigates to a virtual page and asserts the *previously* active row is no longer `is-active`. Asserting that the new row **is** active only covers the pages whose rel appears in the nav; asserting the old one is not covers all of them.

## Fixed 2026-08-18

Nine call sites now go through `commitVirtualPage`, which does the five things each branch did by hand and the sixth every copy had lost — `refreshActiveNavRow()`.

Hoisted rather than fixed nine times, because the duplication is what lost the line. `test_every_virtual_page_refreshes_the_nav_highlight` fails on any branch that commits `currentRel` by hand again, which is the shape of the regression rather than its symptom.
