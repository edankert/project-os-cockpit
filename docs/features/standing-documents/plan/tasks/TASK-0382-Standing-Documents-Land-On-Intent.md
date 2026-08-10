---
type: "[[task]]"
id: TASK-0382
aliases: ["TASK-0382"]
title: "The Intent view opens on the standing documents, each showing when it was last confirmed"
status: done
phase: "[[PHASE-030-Obligations-Go-Home]]"
owner: user:edwin
created: 2026-08-10
updated: 2026-08-10
source: ["[[REQ-0033-Every-Project-Can-Say-What-It-Is]]"]
parent: "[[FEAT-0091-The-Standing-Documents]]"
effort: M
due: ""
depends: ["[[TASK-0380-The-Manifest-As-Data]]"]
blocks: []
related: ["[[FEAT-0087-Design-Widens-Into-The-Projects-Constraints]]", "[[FEAT-0089-The-Obligation-Registry-And-The-Badges]]", "[[REQ-0025-No-Type-Loses-Its-Surface]]"]
tests: []
---

# Standing documents land on Intent

## Definition of Done
- [x] The Intent view's landing is the standing set — the documents answering *what is this project*, in the order the manifest declares — `What this project is`, first group, all eight entries (`test_the_intent_view_opens_on_the_standing_set`)
- [x] Each entry shows when it was last confirmed, and reads differently when stale, stubbed or missing — the row's status comes from the finding kind, its subtitle from the finding's own words
- [~] A stale standing document is an obligation kind in [[FEAT-0089]]'s registry, owned by Intent and counted in its badge — **missing, ambiguous and stub count; stale marks and does not**, for the reason below
- [x] They are reachable here, not only through the Library file tree — closing the gap [[REQ-0025]] recorded
- [x] The set is not listed anywhere else; Library keeps showing the *files*, which is a different question — asserted across every view (`test_the_standing_set_is_not_a_second_obligation_list`)

## Steps
- [x] Render the manifest as the Intent view's landing
- [x] Register the standing set as an obligation with Intent as owner — declared beside the type-keyed table, not inside it
- [x] Check against [[REQ-0025]]'s guard that nothing loses its only surface

## Notes
This is the "prominent place" Edwin asked for, and it also settles the empty-state question for the Intent view — the view about what the project *is* opens on the documents that say so. Two answers, one surface, which is why the landing is not a separate design decision.

**Not a second list.** Library shows these as files in a tree ([[ISS-0125]] keeps that overlap deliberately); Intent shows them as the project's own answer, with their freshness. One item, two addresses, on the boundary [[FEAT-0087]] already records.

Making staleness an obligation kind is what stops this being a decorative panel: it inherits the badge, and the badge is the thing that gets looked at.

## Done 2026-08-10

### Where the DoD was narrowed, and why

The criterion said *"a **stale** standing document is an obligation kind"*. It is not, and the line drawn instead is: **missing, ambiguous and stub are owed; stale marks the row.**

Each of the first three is binary and one act clears it — write the document, delete the rival, fill in the template. Staleness returns by the calendar: counting it is a badge that re-arms itself forever, which is the permanent nag this project has been bitten by twice (PHASE-015's close-out pill, and the `Doing · 44` that had one real item). A stale document still renders with `review` status and *"last confirmed 196 days ago"* in its subtitle; it simply does not ask.

Measured here, which is what makes the line concrete rather than cautious: **ARCHITECTURE and OWNERSHIP hold their templates** (owed), **DESIGN and STYLEGUIDE were last confirmed 196 days ago** (marked). Four of eight have something wrong; two of eight ask for something.

Reconciled rather than ticked, because it is a change to what the note said and should read as one.

### The registry needed a second shape, not a stretched first one

`architecture`, `glossary` and `reference` each declare `NONE` in the type-keyed table, and correctly — 11 notes are in this repo's Reference group and only 5 are project singletons, so making the **type** owed would count the wrong population. The subject of this obligation is a **manifest entry**, which a table keyed by note type cannot express.

So `STANDING_OBLIGATION` is declared beside the table rather than forced into it, and `counts()` adds it to the same total. `badges_payload`'s total is still the sum of the badges — asserted, because the whole reason [[FEAT-0089]] exists is that a number must not disagree with itself on one screen.

### Not a second list

`test_the_standing_set_is_not_a_second_obligation_list` sweeps every view and fails if any other group marks one of these as owed. The Library still shows them as **files in a tree** — [[ISS-0125]] keeps that overlap deliberately — and that is a different question from *what does this project say it is*. [[ISS-0068]] forbids one obligation with two homes, not one document with two addresses.

### Verification

`919 passed, 2 skipped`; `validate-docs: OK`. Four new assertions; three design-bench tests updated, since they asserted the design mode's group list exactly and the standing group is now first.

Adequacy by mutation:

| mutation | killed by |
|---|---|
| add `stale` to the owed kinds | `test_a_stub_is_owed_and_staleness_only_marks` |
| stop adding the standing count to the badge | `test_the_standing_obligation_reaches_the_intent_badge` + 1 |
