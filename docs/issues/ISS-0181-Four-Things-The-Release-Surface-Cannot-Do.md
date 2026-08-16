---
type: "[[issue]]"
id: ISS-0181
aliases: ["ISS-0181"]
title: "Four things the release surface cannot do — mark a check intentionally left open, attach text to one, edit without the page reloading under you, or complete a release"
status: "open"
phase: "[[PHASE-999-Future]]"
owner: user:edwin
created: 2026-08-16
updated: 2026-08-16
source: ["Edwin 2026-08-16, using the rebuilt Publication view: 'The acceptance tests do not support the new intentionally left open option and do not support adding text, also the save / reload functionality is really annoying. Also, it might make sense to make it possible to complete the release from the release note?'"]
severity: high
component: desktop-renderer
parent: ""
related: ["[[FEAT-0104-The-Suite-Is-The-Surface]]", "[[FEAT-0107-Publication-Is-A-List-Of-Releases]]", "[[ISS-0177-An-Exception-Mark-Drops-A-Check-With-No-Justification]]", "[[ISS-0175-The-Nth-Checkbox-Is-Not-The-Nth-Task-Line]]"]
tests: []
---

# Four things the release surface cannot do

Reported from use, all four functional rather than cosmetic.

## 1. A check cannot be marked intentionally left open

`[!]` — the release exception — exists in the parser, counts correctly, and is settable **only by hand-editing the file**. [[FEAT-0104]] designed the interaction and it is deferred behind [[ISS-0175]]: the rendered document's checkbox order does not match the acceptance tests' own, so a control keyed on checkbox position would write to the wrong check.

Worth stating plainly: the *permissive* half is already live ([[ISS-0177]]). A hand-written `[!]` drops a check from the gate today, with no justification and nothing owed. So the capability exists and only the safe way to reach it is missing.

## 2. A check cannot carry text

No justification, no evidence, no note. `TESTING.md` line 113 requires a justification for every exception, and there is nowhere to put one except the file. The same gap makes a *passed* check unable to record what was observed — which is what `REQ-0028` means by acceptance naming who stood behind it.

## 3. Editing is interrupted by save/reload

Ticking a checkbox writes the file, the watcher fires, and the page re-renders. Edwin: *"the save / reload functionality is really annoying."* On a 1082-line document with 542 checkboxes, walking a section means being interrupted on every single tick.

## 4. A release cannot be completed

The lifecycle is `open → preparing → released` and **nothing performs the last transition**. `TESTING.md` rule 5 says what shipping actually entails — Tier 3 tests removed, `RE-RUN` annotations cleared — and `features:` freezing and the acceptance-test snapshot being recorded are two more. All manual, which is why 5 of `your-trainer`'s 12 releases have `tests_verified:` empty and 53 stale `RE-RUN` annotations have accumulated.

Edwin's suggestion: do it from the release note.
