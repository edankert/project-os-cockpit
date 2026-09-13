---
type: "[[task]]"
id: TASK-0621
aliases: ["TASK-0621"]
title: "The release rung, the release page and the checks page point at the walk while a release is draft, and none of them gains a mark"
status: done
phase: "[[PHASE-043-The-Walk-Page]]"
owner: user:edwin
created: 2026-09-13
updated: 2026-09-13
source: ["[[FEAT-0149-The-Walk-Page]]"]
parent: "[[FEAT-0149-The-Walk-Page]]"
effort: S
due: ""
depends: ["[[TASK-0619-The-Walk-Page]]"]
blocks: []
related: ["[[ADR-0035-A-Release-Page-Reports-It-Does-Not-Record]]", "[[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]", "[[FEAT-0102-Publication-Becomes-A-View]]"]
tests: ["[[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]]"]
tags: [task, publication, renderer]
---

# The release rung points at the walk

## Why

A page nobody can reach is a page nobody walks. The release rung already says how many checks are owed; the release page's gate row and the checks page's header say it again. Each of those sentences becomes the door to the walk, and only while a release is `draft`, because that is when a walk exists to do ([[ADR-0028-Work-Has-Three-Phases]]: the gate asks only while a release is in preparation).

## Definition of Done

- [x] The release rung in the publication ladder reads "N owed · walk them" beside its existing count while the release is `draft`, and the phrase is a link to `~walk/<platform>` for that release's platform. When nothing is owed it reads as it does today.
- [x] The release page's gate row carries the same link. The settle section is unchanged: still `na`, `excused`, `blocked` only, still no `pass` ([[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]). The "Still to check for these contents" list is unchanged.
- [x] The checks page header gains "walk them" beside "N unwalked — a release is blocked" while a release is `draft`, linking to the walk for the open release's platform. With no draft release the header is as it is today.
- [x] No mark control is added to the release page or the ladder. A source guard asserts that `renderReleasePage`'s body does not call `askForMark` with a `pass` in `only:`, which is the existing guard extended to cover the new link.
- [x] A repo with two open ledgers: the rung links to its own release's platform; the checks page links to the platform the acceptance route resolves by default. A picker is not built; the choice is recorded in this note.
- [x] Visual evidence in `docs/attachments/` for the ladder with the link, the release page's gate row, and the checks header, captured the way FEAT-0066 captures a surface, referenced from this task's walk note.

## Steps

- [x] Read `renderReleasePage` (`desktop/src/renderer/renderer.ts`, from the `async function renderReleasePage(` line) and the "what is still owed FOR THOSE CONTENTS" block below it, which is where the gate row and the open-tests list are built.
- [x] Read the ladder builder that renders the release rung (FEAT-0102's `TASK-0428`), and add the link where the owed count is printed.
- [x] Read `buildChecksPage`'s header (`state.textContent = v.blocking ? …`) and append the link when `open_releases` is non-empty.
- [x] Add `walkLink(platform)` as one helper the three call, so the address is built in one place.
- [x] Renderer-harness tests beside `tests/test_checks_view.py` and the release page tests: the link appears with a draft release and not without; the settle section's `only:` is unchanged.

## Notes

**Why last.** [[FEAT-0102-Publication-Becomes-A-View]] records the rule twice: a permanent blank button is the failure. The link lands only once [[TASK-0619-The-Walk-Page]] has a page behind it.

**Why not replace the "Still to check" list.** That list is the subtraction [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] built: the checks covering features this release carries, three rows on `your-trainer` against fifty-nine in the gate. It answers a different question from the walk, which is every owed check in order. Both stay.

## Done 2026-09-13

Three doors, one address. `walkLink(platform)` is the only place a walk address is spelled, and a test asserts there is no second one.

- **The publication ladder's release rung** gains a `Walk them` row under Acceptance tests: *"39 owed on android — the checks in walking order, each with its setup, steps and expected result"*.
- **The release page's gate section** gains `N owed · walk them`. It records nothing new: the settle section still offers `na`, `excused` and `blocked` only, and `tests/test_release_held_back.py`'s universal claim over every release surface still passes unchanged.
- **The checks page header** gains `walk them` beside its unwalked count.

Each appears only while there is a walk to do, and the rows in `tests/test_walk_links.py` are the four ways there is not: nothing owed, a shipped release, a release naming a platform the repo keeps no ledger for, and a payload that names no platform at all.

### Decisions taken here

- **No platform picker.** The rung links to its own release's platform and the checks page links to the platform its payload resolved, which for an absent parameter is the open release's ([[ISS-0289]]). A repo with two open ledgers gets two walks reached from two rungs, which is the shape `ledger.owed` already has.
- **The rung's number is the walk's own.** `unchecked` where that row is built is the union across every ledger — 327 on `your-trainer`, whose open Android release owes 39 — so reading it would have put two answers to one question a click apart. The row takes the platform-scoped count, and a test asserts it equals what the walk payload returns.
- **The "Still to check for these contents" list stays.** It answers a different question — the checks covering the features *this* release carries, three rows on `your-trainer` against 39 in the gate — and [[ADR-0040-A-Release-Selects-Its-Features-Not-Its-Excuses]] built it deliberately.
- **Visual evidence** is the screenshot on [[TST-0088-The-Walk-Page-Hands-Over-The-Owed-Checks]], which shows the walk opened from the ladder's row.
