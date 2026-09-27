---
type: "[[issue]]"
id: ISS-0316
aliases: ["ISS-0316"]
title: "The Tests page lists a check under Regression tests even when the check says kind: feature"
status: fixed
phase: []
owner: user:edwin
created: 2026-09-27
updated: 2026-09-27
source: ["project-os-dev ISS-0104, from your-trainer ISS-0414, decided by Edwin on 2026-09-27: 'ISS-0414: take your recommendation, option 1'"]
reported_by: user:edwin
question: ""
severity: medium
component: "acceptance"
parent: ""
related: ["[[project-os-dev#ISS-0104]]"]
tests: []
---

# The Tests page lists a check under Regression tests even when the check says kind: feature

## Problem

The template now lets an acceptance check declare `kind: feature` or `kind: regression`, and the declared kind wins over the one its `covers:` gives (project-os-dev ISS-0104). The cockpit works out a check's kind in its own `acceptance.kind_of`, which reads only `command:` and `covers:`. So a check with `covers: [ISS-0387]` and `kind: feature` would sit under Regression tests on the Tests page, and an invalidation of it would never show it as stale. `release-test.py` and the validator would call it a feature check, so the two surfaces would disagree.

## Expected

`kind_of` gives the declared kind when the note has one, after `command:` and before `covers:`, as `TESTING.md`, "The three test kinds", says.

## Next Actions
- [x] `acceptance.kind_of` reads `kind:` from the note, with a test that fails without it.
- [x] Refresh the bundled `release_test_bundled.py` and `validate_docs_bundled.py` from the template sync.

## Fixed, 2026-09-27

`acceptance.kind_of` now returns the declared kind after `command:` and before `covers:`, and `item_from_note` reads `kind:` into `Item.declared_kind`. Because the navigator's `_covers_an_issue` asks `kind_of`, the Tests page and the generated page move such a check to Feature tests together. Four cases in `tests/test_invalidation_scope.py` cover it: `kind: feature` beside an `ISS-*` makes the check a feature check that an invalidation reopens, `kind: regression` is honoured, a `command:` still wins, and an unknown value falls back to `covers:`. With the `kind_of` branch removed, the first two fail. The validator's new CHECK-KIND code has a label on the Fleet health page (`desktop/src/renderer/validation-rows.ts`), which the desktop suite requires of every code.
