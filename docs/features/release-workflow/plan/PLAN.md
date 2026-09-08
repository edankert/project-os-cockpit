---
type: "[[plan]]"
title: "Preparing a release is one workflow — delivery sequence"
status: active
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
implements: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"]
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0041-A-Release-May-Settle-A-Check-It-May-Never-Pass-One]]"]
---

# Preparing a release is one workflow

Eight tasks in four pairs. Each pair is a server half and the surface that uses it, and the server half lands first in every case — a control drawn against an endpoint that does not exist is how the *Name the version* button came to send no platform for three weeks after `create_release` learned to accept one.

## Delivery sequence

1. **[[TASK-0597]] — the platform is offered, not typed.** `publication.platform_candidates(index)`, surfaced as the **`platforms`** key on `release_payload`. *(The plan called the key `platform_candidates` too; the function is named for what it computes and the key for what it is, which is how `contents_candidates` and `contents_candidates` already read on the same payload.)* Pure read; nothing else depends on a decision.
2. **[[TASK-0598]] — a release's version and platform can change.** `note_writes.update_release` behind `POST /api/notes/release-update`, with `create_release`'s refusals reused rather than re-derived.
3. **[[TASK-0599]] — a prepared release is abandoned, not deleted.** `note_writes.abandon_release` behind `POST /api/notes/release-abandon`, plus the narrow delete. **This one lands upstream first**: `abandoned` is a new value in a template-owned status vocabulary, so `~/Dev/repos/project-os` changes before anything here writes the status.
4. **[[TASK-0600]] — the version and the platform are named on the release page.** The renderer half of 1–3.
5. **[[TASK-0601]] — the owed checks are settled where they are owed.** `POST /api/notes/release-settle`, and the rewrite of `test_no_write_path_to_a_check_appears_on_the_release_page` that [[ADR-0041]] requires.
6. **[[TASK-0602]] — the walk is one screen.** The owed list on the release page, grouped by area, each row carrying its own procedure text. This is the surface [[ADR-0041]] authorises and the payment of ADR-0035's second objection.
7. **[[TASK-0603]] — the coverage gap is computed, not guessed.** `publication.coverage_gaps` and its section on the release page.
8. **[[TASK-0604]] — an agent drafts the missing checks; a person accepts them.** A `release` entry in `agent_actions.DEFAULT_ACTIONS` with a `commission-checks` verb, and `REL` in the renderer's `NOTE_TYPE_BY_PREFIX` so the verb resolves.

## Dependencies

- **Hard:** [[ADR-0041]] gates tasks 5 and 6, and only those. Nothing else in this plan touches a check.
- **Hard:** task 3's upstream leg (`~/Dev/repos/project-os` `STATUSES.md` and `validate-docs.py`) lands and syncs down **before** any note here carries `status: abandoned`. This repo carries no permanent template divergence, and a status the local validator accepts but the fleet's does not is exactly the drift [[PHASE-041]] closed.
- **Hard:** task 7 lands before task 8. The agent verb's prompt names the uncovered features, and it has nothing to name until the sweep computes them.
- **Soft:** 1 before 4, 2 before 4, 5 before 6 — the server half before the surface, every time.
- **Soft:** task 6 needs the release payload to carry each owed check's procedure text. `Item.text` holds it and `open_tests` does not currently emit it; widening the payload belongs to task 6, not to task 5.

## Open questions

- **Does an abandoned version become reusable?** [[REQ-0061]] criterion 3 says "not silently reusable" and this plan reads that as: `create_release` keeps refusing a version at or below the newest **released** one, and an abandoned draft's version is refused with a message naming the abandoned note, so a deliberate reuse is possible and an accidental one is not. If Edwin wants an abandoned version permanently burned, that is a different refusal and a one-line change.
- **The filename is not renamed when the version changes.** `REL-0013-v2.1.7.md` carries the version in its stem and every `[[REL-0013-v2.1.7]]` in the corpus resolves by that stem. Task 2 reports the stale filename rather than renaming; whether a rename-with-link-rewrite is worth building is a separate decision.
