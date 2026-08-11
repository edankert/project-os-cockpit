---
type: "[[feature]]"
id: FEAT-0072
aliases: ["FEAT-0072"]
title: "The release surface — done-but-unshipped becomes a number, drafting a release becomes an action, and the acceptance-tests gate finally renders"
status: done
phase: "[[PHASE-026-The-Returning-Human]]"
owner: user:edwin
created: 2026-08-03
updated: 2026-08-11
source: ["[[DES-0008-The-Returning-Human]]"]
goal: "An UNRELEASED record card counting features done since the last REL note; Draft-release scaffolds the REL from them as a draft for the actuator row; the REL note view surfaces the acceptance-tests template's own release gate."
requirements: []
tasks:
  - "[[TASK-0315-The-Unreleased-Card]]"
  - "[[TASK-0316-Draft-Release]]"
  - "[[TASK-0317-The-Gate-Band]]"
release: "[[REL-0001-The-Human-Has-Levers]]"
related: ["[[FEAT-0064-The-Acceptance-Gate]]"]
tests: []
---

# The release surface

## Goal

"Done" and "shipped" are different facts and the cockpit knows only one — while the acceptance-tests template has carried a release gate since it was written ("a release is blocked while any Tier 1/2 test is unchecked") with nowhere to bite. REL notes exist as a type with a counter at zero; this is their minimal, honest surface.

## Out of Scope

- Performing releases. The cockpit records that one was cut; pushing and deploying remain a person's deliberate acts (FEAT-0055's line).
- Versioning policy. The REL template's fields; not this feature's opinion.

## Acceptance

- [x] Done-but-unshipped is a number on a surface — `Unreleased · 70` on the overview's record column, absent at zero ([[TASK-0315]])
- [x] It counts membership, not dates: a feature is shipped when a `[[release]]` note names it, and **only a `released` one ships anything** — drafting must not empty the card, because `draft` means *"prepared and verified, not yet live"*
- [x] Its rows navigate — verified by clicking FEAT-0001 through to `features/render-server/FEAT-0001-Render-Server.md`
- [x] Drafting a release is an action that **publishes nothing** — allocates an id, writes one file, `status: draft`, `date: ""`; a test reads every note before and after and asserts nothing else moved ([[TASK-0316]])
- [x] The drafted note lists exactly what the card showed — one computation, handed to the writer, rather than derived twice
- [x] The acceptance-tests gate renders in the template's own words ([[TASK-0317]], done 2026-08-10)
- [~] *"Since the last release"* names an actual release — **reconciled, not ticked**: this project has never shipped one, so the card reads *"70 features done, none in a shipped release yet"* rather than naming something that does not exist. The `since` half is implemented and tested against a built `released` note (70 → 59); it has simply never had live data. It ticks the day REL-0001 ships.

## Verification

`tests/test_unreleased.py` — 10 tests. The one worth naming builds a **shipped** release explicitly, because no release in this corpus has ever been `released` and the subtract-shipped branch therefore never runs here. It was broken when first written (a `NameError` on an unimported helper) and every test against the live corpus stayed green.
