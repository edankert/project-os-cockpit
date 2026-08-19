---
type: "[[issue]]"
id: ISS-0234
aliases: ["ISS-0234"]
title: "The generated acceptance page leads with a tier number, draws two progress bars, and ends every row with information the row already carries"
status: fixed
owner: user:edwin
created: 2026-08-19
updated: "2026-08-19"
severity: medium
component: cockpit-desktop
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
related: ["[[ISS-0223-The-Bar-Is-The-Wrong-Instrument-In-The-Editor]]", "[[ISS-0228-The-Test-Id-Renders-Twice-On-A-Row]]", "[[DES-0012-Tests-In-Two-Flows]]"]
---

# Less on the page, and the id where a reader looks

Edwin, 2026-08-19.

1. **The tier numbers go.** Same reason as the nav: [[DES-0012]] D3 found they name *why a test was created*, not what it tests. `Feature tests`, `Regression tests`, `Verification tests`.
2. **The `TST-*` id at the start becomes a link** to the check's note. [[ISS-0228]] made it selectable; it should also be the way in.
3. **The trailing block goes** — the area suffix and the `open` button. The area is the heading the row sits under, and the id is now the way in. Edwin: *"this is not available in future tests"* — the area suffix exists because [[TASK-0513]] flattened the headings away and it had to go somewhere; the headings are back.
4. **The percentage moves onto the area heading**, right-aligned against the name.
5. **Both progress bars go** — the tier's and the surface's. [[ISS-0223]] replaced the surface bar with a percentage and kept the tier's; this removes both, because the page is worked rather than scanned and the heading now carries the number.

## Done when

- [x] No tier number on the page.
- [x] The id at the start of a row opens the note.
- [x] A row ends after its own content.
- [x] Each area heading carries its percentage, right-aligned.
- [x] No progress bar on this page.

## Fixed 2026-08-19
