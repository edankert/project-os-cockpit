---
type: "[[issue]]"
id: ISS-0268
aliases: ["ISS-0268"]
title: "On a platform release, the navigator can say \"Nothing unshipped\" while the Unreleased card lists features, and drafting a release puts other platforms' features into the note"
status: open
owner: user:edwin
created: 2026-08-30
updated: "2026-09-19"
severity: medium
component: cockpit
phase:
source: ["Independent review of 46d6593..c861414, 2026-08-30, model:claude-opus-5, fresh context"]
related: ["[[ISS-0261-A-Release-Is-Offered-Features-Its-Platform-Cannot-Ship]]", "[[TASK-0587-The-Derived-Set-Is-This-Releases-Platforms]]", "[[FEAT-0142-A-Release-Says-What-Is-In-It]]"]
tests: []
reported_by: review
---

# The navigator and the release draft ignore the release's platform

With an Android release open, the left pane can say "Nothing unshipped" while the Unreleased card lists iOS features that are waiting, and **Draft release note** writes those iOS features into the new Android release.

[[ISS-0261]] scopes `shipping_in` and routes the release page and the navigator through it. Three consequences of that scoping were not followed through, and one of them is a sentence the app now says that is false.

## 1. `Nothing unshipped` is now reachable while work is unshipped

`_publication_groups` renders a placeholder row when `_next_ids` is empty, and `_next_ids` is now the **platform-scoped** set while the row's text was written against the fleet-wide one. Constructed and run against `c861414` — one `platform: android` release, two `done` iOS features, nothing else:

```
Unreleased card says: 2 ['FEAT-0001', 'FEAT-0002']
Navigator 'Next release' items: [{"title": "Nothing unshipped",
                                  "subtitle": "no features are waiting on a release", ...}]
```

Two surfaces of the same app, one saying nothing is waiting and the other listing two. `../your-trainer` does not show it today only because four features survive its scoping; it shows it the moment those four ship. This is the failure mode TASK-0587 named when it changed `contents["count"]` to `len(derived_rows)` — *"a heading that disagrees with the rows beneath it is worse than either number alone"* — arriving on the surface that was not changed.

## 2. Drafting the release writes the unfiltered set into the note

[[ISS-0261]] discloses `server.py`'s `create_release` as a third reader and calls leaving it alone correct, *"under the opt-in rule a release that has not said what it ships correctly takes everything"*. What the note does not say is that this is the path by which the reported symptom comes back and becomes durable.

**Draft release note** on the Unreleased card posts `{type: 'release', title}`; the server computes `features` from `cockpit.unreleased_payload(index)` — unfiltered — and stamps all of them into the new note. `release_payload` then sees a non-empty `features:` and switches to `kind: "chosen"`, rendering exactly those rows. So on `../your-trainer` the reader is shown a correctly scoped list of 3, drafts the release from the card, and the new REL note names 13 features including the nine iOS ones and `FEAT-0098` — now as *chosen* contents rather than derived ones, which is a stronger claim than the one that was wrong.

`note_writes.mark_released` then freezes that `features:` list, so an Android release ships iOS features and they leave the Unreleased card as delivered. That half is pre-existing and is not a regression; what is new is that the fix reads as complete while the front door beside it is unfixed.

## 3. `mark_released` changed behaviour and no note says so

`note_writes.mark_released` already called `publication.shipping_in(index, release_id)` for its fallback frozen list. It is a fourth reader, it now freezes a platform-scoped set, and neither ISS-0261 (*"the set had three readers"*) nor TASK-0587 mentions it. The new behaviour looks right — a release should freeze what it could carry — but it arrived silently, and `mark_released` is the one write in the repo that seals a record.

## Next Actions

- [ ] Give the placeholder text the scope it now describes, or key it on the unscoped set.
- [ ] Decide what `create_release` writes: either take a platform on the way in, or filter after the note exists and its `platform:` is known.
- [ ] Say in TASK-0587 that `mark_released` is the fourth reader and that its frozen list moved.

## Checked against the code, 2026-09-19: still true, kept

**What a user notices:** two parts of the app disagree about whether anything is waiting to ship. A release drafted from the card claims features its platform cannot ship, and marking it released records them as delivered.

Evidence: `src/project_os_cockpit/cockpit.py:4920-4921` builds `_next_ids` from the platform-scoped `shipping_in`, and `:4963-4966` still shows "Nothing unshipped / no features are waiting on a release" when that list is empty. `src/project_os_cockpit/server.py:2300-2302` still fills a drafted release's `features:` from the unfiltered `cockpit.unreleased_payload(index)`, even though it now passes a `platform` (`:2314`) to `note_writes.create_release`. Part 3 (TASK-0587 not naming `mark_released` as a reader, `note_writes.py:2300`) is a documentation gap only.

**Small fix:** no. There are two separate fixes (the placeholder text in `cockpit.py`, and filtering the drafted features by platform in `server.py`), each needing its own test.

**Belongs to:** FEAT-0142 (A release says what is in it). **Next:** filter the drafted features through `shipping_in` once the platform is known, and reword the placeholder to name the platform.

Checked as part of project-os-dev FEAT-0036 (TASK-0141).
