---
type: "[[issue]]"
id: ISS-0263
aliases: ["ISS-0263"]
title: "Marking a check navigates the reader to the Tests landing — `~checks` belongs to the Tests view, but the landing guard recognises only `~tests`, so every note write evicts the reader mid-walk"
status: fixed
owner: user:edwin
created: 2026-08-30
updated: 2026-08-30
severity: high
component: ui
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
fixed_in: "[[TASK-0589-A-View-Knows-Which-Pages-It-Owns]]"
source: ["Edwin, 2026-08-30, third report of one symptom: 'It still moves away from the acceptance checks page to the tests section/needs you section?'"]
related: ["[[ISS-0262-Marking-A-Check-Clears-The-Filter-You-Are-Walking]]", "[[ISS-0193-The-Landing-Painted-Over-The-Checks-Page]]", "[[ISS-0068-One-Corpus-In-Two-Places]]", "[[FEAT-0092-The-Views-Get-A-Page]]"]
---

# A write evicts the reader from `~checks`

## The chain

1. Mark a check → the server writes the note.
2. The watcher emits `file-changed`.
3. `scheduleSoftReload` calls `loadWsNav()`.
4. `loadWsNav`'s landing guard reads `if (currentRel !== '~tests')` → from `~checks` that is **always** true → `navigateTo('~tests')`.

So every tick threw the reader onto the Needs-you landing. Nothing about the mark path is special; **anything** that refreshes the navigator while `~checks` is open does it, including an edit made in another editor.

## Why the earlier fix was not this

[[ISS-0262]] was real and is fixed — marking also cleared the tier and area filters, because the address-driven render was being used as the post-write repaint. But it was a **second** defect on the same keystroke, and fixing it left the eviction untouched. Reported three times before the cause was found, twice against a plausible-but-wrong explanation offered from reading the code rather than from reproducing it. The lesson is in the count.

`scheduleSoftReload` already special-cases `~overview` to refresh in place — *"scroll survives, no history churn"* — which is the same reader-holding concern arriving at the same function, and `~checks` was simply never added.

## The actual defect

**A view with two pages was landed as though it had one.**

`~checks` lives inside Tests on purpose: giving the acceptance suite its own nav mode would put one corpus in two places, which is [[ISS-0068]]. `VIEW_LANDING_RELS` then models each of `~features`, `~issues`, `~tests` as a view with exactly one page, and asks `currentRel !== target`.

Publication and Design do not have this bug, and the reason is instructive — both guard on their whole family (`!currentRel.startsWith('~release')`, `!currentRel.startsWith('~design')`) because both were built knowing they had a list *and* a page. The three `VIEW_LANDING_RELS` views were built as single-page and one of them grew a second page later.

## Fix

`VIEW_OWNED_PAGES` — the pages a view owns besides its own landing, `tests: ['~checks']` — and `onOwnedPage(navMode, rel)` replacing the equality test. `~checks`, `~checks/tier/2` and `~checks/area/Monetization` all now read as *already on this view*.

Guarded two ways: reverting the guard to the equality test fails `test_a_write_does_not_evict_the_reader_from_the_checks_page`, and a second test pins that a reader who is genuinely elsewhere still gets landed, so the fix cannot quietly undo [[FEAT-0092]].
