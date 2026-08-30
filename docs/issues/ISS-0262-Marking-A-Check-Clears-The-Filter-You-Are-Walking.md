---
type: "[[issue]]"
id: ISS-0262
aliases: ["ISS-0262"]
title: "Marking a check on `~checks` clears the tier and area the reader was walking — the address-driven render is used as the post-write repaint, so every tick puts the whole suite back"
status: fixed
owner: user:edwin
created: 2026-08-30
updated: 2026-08-30
severity: medium
component: ui
phase: "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"
fixed_in: "[[TASK-0588-A-Write-Is-Not-A-Navigation]]"
source: ["Edwin, 2026-08-30, walking v2.1.7's suite in ../your-trainer: 'When selecting/checking an acceptance test, it moves away from the list of acceptance tests and makes me having to move back to them again, this is really annoying if you want to do multiple checks at the same time.'"]
related: ["[[ISS-0203-The-Tier-Filter-Was-Sticky]]", "[[ISS-0188-The-Scroll-Fix-That-Did-Nothing]]", "[[FEAT-0114-The-Acceptance-Suite-As-A-List]]"]
---

# A write is treated as a navigation

## What happens

`~checks` is built to be *walked*: filter to a surface, then tick your way down it. Every tick threw the filter away.

`renderChecksPage(tier, area)` is the **address-driven** entry point. It sets both filter axes unconditionally, and that is correct where it lives — arriving at a bare `~checks` must not inherit the previous page's filter, which is [[ISS-0203]].

`markCheckRow` handed that same function to `walkOneCheck` as its **repaint**:

```ts
async function markCheckRow(item: GateItem): Promise<void> {
  await walkOneCheck(item, renderChecksPage);   // ← no address
}
```

So each mark ran it with `tier=''`, `area=''` and cleared `checkFilters.tiers` and `checkFilters.areas`. Walking a filtered surface — the way the page is meant to be used — put the whole 623-row suite back after every single tick.

The retire path had the same shape, one line of `await renderChecksPage()`.

## Why the scroll fix could not save it

`walkOneCheck` already holds `docView.scrollTop` across the repaint, twice, once synchronously and once inside the frame — three rounds were spent earning that property on the document surface ([[ISS-0188]]). It was never the problem here and could not have been: **holding a pixel offset is meaningless once the list under it is a different list.** The reader was not scrolled away, they were shown something else.

Worth recording because the symptom — *"it moves away from the list"* — reads exactly like a scroll defect, and the scroll code is the first place anyone looks.

## Fix

Split the two callers apart rather than making one function guess which it is:

- `renderChecksPage(tier, area, { keepFilters })` — the reset is now behind an opt-out, and the default is unchanged, so navigation behaves exactly as it did and `ISS-0203` does not come back.
- `repaintChecksPage()` — a named function for the post-write path, used by both `markCheckRow` and `retireCheckRow`.

Named rather than inlined at each call site because there are two write paths and there will be a third, and the next one should find the correct helper sitting beside the wrong one.

## Guards

Three, in `tests/test_checks_view.py`, and the first fails when the repaint callback is put back to `renderChecksPage` — the original defect, reproduced exactly. The second forbids a bare `renderChecksPage()` anywhere in the renderer rather than naming the two known sites, because a new write path copying the old shape is how this would regress. The third asserts the address still wins on navigation, so the fix cannot quietly become `ISS-0203`.
