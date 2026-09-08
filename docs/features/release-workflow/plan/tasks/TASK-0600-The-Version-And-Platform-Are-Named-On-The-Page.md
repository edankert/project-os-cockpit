---
type: "[[task]]"
id: TASK-0600
aliases: ["TASK-0600"]
title: "The version and the platform are named on the release page — a picker beside the version field, a Platform row on an open release, and Abandon on a draft"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: M
due: ""
depends: ["[[TASK-0597]]", "[[TASK-0598]]", "[[TASK-0599]]"]
blocks: []
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ISS-0288-The-Release-Gate-Ignores-The-Release-Platform]]", "[[ISS-0139]]"]
tests: []
---

# The version and the platform are named on the release page

The renderer half of [[TASK-0597]], [[TASK-0598]] and [[TASK-0599]].

**The defect this fixes first.** `buildReleasePage`'s *Name the version* control posts `{ version, actor: 'user:edwin' }` to `/api/notes/release-prepare` and nothing else. `create_release` learned to accept a `platform:` under [[ISS-0290]] — so every release created through the tool since then has arrived platform-less anyway, because the only caller never offers one. The picker is not a convenience; it is what makes the server-side field reachable.

## Definition of Done

- [x] A platform picker sits **beside** the version field in `buildReleasePage`'s *Name the version* block, populated from `d.platforms` (the key `publication.platform_candidates` fills), defaulting to *every platform*.
- [x] The submit sends the chosen platform, and the release note written by it carries the field.
- [x] An **open** release renders a `Platform` row showing the current value and offering the same picker, posting to `/api/notes/release-update`.
- [x] The version on an open release is editable through the same endpoint, and the page shows the filename-still-names-the-old-version notice the write returns.
- [x] A **draft** release offers **Abandon**, which demands a reason before it will submit and offers an optional *superseded by* field.
- [x] **Every refusal renders beside the control that caused it**, never in a toast. The page already does this — `buildReleasePage` builds an `.ask-error` paragraph directly under the version field, with a comment stating why: *"rather than in a toast that disappears before it has been read"*.
- [x] **Nothing this task adds pops a dialog.** Version, platform, abandon and delete are all inline: the abandon reason is a `textarea` on the page with an optional *superseded by* beside it, and delete is a two-click arm-then-confirm whose warning renders in the same `.ask-error` paragraph as every other refusal.

  *(The page as a whole is not yet free of them, and ticking this box for the whole page would be false. `buildReleasePage`'s **Record what it verified**, `holdFeatureBack`'s reason prompt and `fillUnreleasedCard` each still raise `askForText`; all three predate this task and are recorded as a follow-up in [[CHG-20260908-Preparing-A-Release-Is-One-Workflow]]. The settle dialog is a separate matter and is deliberate — [[ADR-0041]] decision 4 requires the check's procedure to be readable where the mark is chosen.)*
- [x] Naming a platform **changes the gate count on screen** without a manual reload. That is [[ISS-0288]]'s consequence made visible to the person who caused it: pick `android` and the number falls from the union to the Android ledger.

## Steps

- [x] Extend `ReleasePayload` in `renderer.ts` with `platform`, `platforms`, `delete_refusal` and whatever `update_release` returns.
- [x] Build the picker as a `<select>`; it is a closed set by construction ([[TASK-0597]]) and a combo box would re-admit the typo.
- [x] Re-render through `renderReleasePage(releaseId)` after every successful write, as the existing submit does.
- [x] Abandon needs a confirmation, and the confirmation is the **reason field**: a control that cannot be submitted empty is its own guard, and one more *Are you sure?* is not.

## Notes

**This task adds no control that touches a check.** The settle buttons are [[TASK-0601]] and [[TASK-0602]], under [[ADR-0041]]. `tests/test_release_held_back.py::test_no_write_path_to_a_check_appears_on_the_release_page` scans every top-level function whose name mentions a release — including any new one this task adds — so a helper introduced here that reaches a check write fails that test immediately, which is the intended behaviour.
