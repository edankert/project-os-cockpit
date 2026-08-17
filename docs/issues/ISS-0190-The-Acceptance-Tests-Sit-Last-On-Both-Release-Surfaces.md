---
type: "[[issue]]"
id: ISS-0190
aliases: ["ISS-0190"]
title: "The acceptance tests sit last on both release surfaces, the delta rows carry three verdict buttons on the right, and the suite is reachable only through a button"
status: "fixed"
phase: "[[PHASE-034-Three-Phases-And-Publication-Is-The-Third]]"
owner: user:edwin
created: 2026-08-17
updated: "2026-08-17"
source: ["Edwin 2026-08-17: 'Can you move the acceptance tests section to the top of the next release section (left pane) since this needs to be completed (the features/issues are things that simply ship with this release), also move it to the top in the overview section. The delta section under the acceptance tests can also become a little nicer and remove the buttons on the right, if you want you can have the checkbox on the left as long as the check box functionality is the same as in the .md file.'", "Edwin 2026-08-17: 'Also remove the open the acceptance tests button, just show this as a file link instead, similar to how the requirements are shown on that page.'"]
severity: medium
component: desktop-renderer
parent: ""
related: ["[[FEAT-0108-The-Gate-Is-A-Delta-Not-A-Census]]", "[[FEAT-0111-The-Marks-The-Record-Already-Uses]]", "[[ISS-0180-The-Release-Page-Printed-What-It-Should-Have-Rendered]]", "[[ISS-0186-The-Mark-Glyphs-Are-Decorative-And-The-Dialog-Is-Too-Narrow-For-Six-Options]]"]
tests: []
---

# The acceptance tests sit last on both release surfaces

## Ordering, and the reason it is not a preference

Both release surfaces put the acceptance tests **last**:

- the navigator's release group builds `Features · N`, `Issues · N`, `Acceptance tests · N`, `Documents · N` in that order (`cockpit.py::_release_content_rows`)
- the release page builds *What's in it*, the recorded tests, *Shipped with*, *Published artifacts*, *Still owed*, and the gate **last** (`renderer.ts::buildReleasePage`)

Edwin's argument for reversing it is the whole point and worth keeping verbatim:

> *"since this needs to be completed (the features/issues are things that simply ship with this release)"*

A feature on a release is a **fact about what is in it**. An unchecked Tier 1 check is **an errand**. The two were ordered by how the record is structured rather than by what the reader has to do, and the errand ended up beneath five sections of inventory. [[FEAT-0108]] moved the gate from a census to a delta so somebody could act on it; putting that delta at the bottom of the page undoes half of it.

## Three verdict buttons on the right, and a control that already exists

Every actionable gate row carried `Pass · Partial · Fail` — three buttons, on the right, in a row whose left column is a check number. Meanwhile [[FEAT-0111]] and [[ISS-0185]]..[[ISS-0189]] built exactly this control for the same rows *in the document*: one mark on the left, drawn from the file, opening one dialog with all six marks and the shared reason field.

So the page had two vocabularies for one act — three verbs here, six marks there — and the smaller one was the newer.

Edwin: *"remove the buttons on the right, if you want you can have the checkbox on the left as long as the check box functionality is the same as in the .md file."*

Same control, same dialog, same write path (`POST /api/notes/mark-check`). What the gate row needs beyond the document row is the **current mark**, which the payload did not carry — `acceptance.Item` computed five booleans from the mark character and then dropped it.

## And the suite was behind a button

`Open the acceptance tests` was a primary button in the middle of the gate section. Every other file on that page — a feature, a published artifact, a verified test — is a **row you click**. Edwin: *"just show this as a file link instead, similar to how the requirements are shown on that page."* One idiom for opening a file, not two.

## Expected

1. `Acceptance tests` is the **first** subgroup of a release in the navigator, before Features and Issues.
2. The gate is the **first** section of the release page, above *What's in it*.
3. Gate rows carry the mark control on the left and no buttons on the right; it shows the mark the file holds, opens the same dialog the document uses, and writes through the same endpoint.
4. Rows that are not a thing to walk — quiet, and stale — show their mark but are not clickable, which is the rule the verdict buttons already followed.
5. The suite opens from a file row, not a button.

## Fixed 2026-08-17
