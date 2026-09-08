---
type: "[[task]]"
id: TASK-0599
aliases: ["TASK-0599"]
title: "A prepared release that will not ship is abandoned, not deleted — `abandoned` joins the release status vocabulary upstream first"
status: done
phase: "[[PHASE-037-The-Surfaces-Report-At-The-Readers-Granularity]]"
owner: user:edwin
created: 2026-09-08
updated: "2026-09-08"
source: ["[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]", "Edwin, 2026-09-08: 'Update and delete release should also be possible'"]
parent: "[[FEAT-0145-Preparing-A-Release-Is-One-Workflow]]"
effort: M
due: ""
depends: []
blocks: ["[[TASK-0600]]"]
related: ["[[REQ-0061-A-Release-Is-Written-Through-One-Workflow]]", "[[ADR-0008]]", "[[PHASE-041-The-Gate-Runs-Where-The-Checks-Are]]"]
tests: []
---

# A prepared release is abandoned, not deleted

Edwin asked for delete. The record says otherwise, and the evidence is one note: `your-trainer`'s **REL-0013** was prepared as v2.1.7, never shipped, and is still `draft` with `superseded_by: [[REL-0016-v2.1.8]]`. That note is the only reason anybody can tell why the version number was skipped. Erasing the file erases the answer.

So the front door is **Abandon** — a terminal status with a reason — and a true delete exists only for the case where nothing has been recorded yet.

## This changes a template-owned vocabulary, so it lands upstream first

`abandoned` is not currently a legal release status anywhere. The allowed set is `{"draft", "released", "reverted"}`, stated in five places:

| file | what it holds |
| --- | --- |
| `~/Dev/repos/project-os/tools/instructions/STATUSES.md` | `## [[release]]` — allowed values and transitions |
| `~/Dev/repos/project-os/tools/scripts/validate-docs.py` | `"release": {"draft", "released", "reverted"}` |
| `tools/instructions/STATUSES.md` (this repo, synced copy) | the same section |
| `tools/scripts/validate-docs.py` (this repo, synced copy) | the same line |
| `src/project_os_cockpit/validate_docs_bundled.py` | the same line, the copy the sidecar runs |

Plus the terminal-status sets the cockpit reads: `src/project_os_cockpit/statuses.py`, `src/project_os_cockpit/cockpit.py` and `desktop/src/renderer/renderer.ts` each carry a list of statuses that mean *finished*, and `abandoned` belongs in all three or an abandoned release will render as live work forever.

**Upstream lands and syncs down before any note here carries the status.** This repo carries no permanent template divergence, and a value the local validator accepts while the fleet's refuses it is exactly the drift [[PHASE-041]] closed. Run `tools/scripts/sync-project-os.sh ../project-os` after the upstream commit.

## Definition of Done

- [x] `abandoned` is a legal `release` status upstream, in `STATUSES.md` and `validate-docs.py`, with the transition `draft → abandoned` documented beside `draft → released`.
- [x] The synced copies here match upstream byte for byte, and `validate_docs_bundled.py` carries the same set.
- [x] `abandoned` is in the terminal-status sets in `statuses.py`, `cockpit.py` and `renderer.ts`.
- [x] `note_writes.abandon_release(index, release_id, *, reason, superseded_by="", actor="", mtime=None)` sets `status: abandoned`, writes the reason into the note, and **refuses without a reason**.
- [x] `superseded_by:` is optional and, when given, must resolve to a note. A release abandoned because it was replaced says what replaced it; one abandoned because the work was dropped has nothing to point at, and demanding a link would produce a fake one.
- [x] A `released` release cannot be abandoned.
- [x] `POST /api/notes/release-abandon` exposes it.
- [x] **A true delete exists and is narrow**: refused unless the note was created today, **and** nothing in the corpus links to it, **and** its platform's ledger holds no entry naming it. All three, or the note stays.
- [x] The abandoned version is not silently reusable: `create_release`'s version refusal names the abandoned note when a version collides with one.

## Steps

- [x] Upstream first: edit `~/Dev/repos/project-os/tools/instructions/STATUSES.md` and `tools/scripts/validate-docs.py`, commit there.
- [x] Sync down; verify the two copies here are identical to upstream's.
- [x] `validate_docs_bundled.py` is this repo's own copy of the validator and is not covered by the sync — edit it in the same commit or the sidecar will refuse a status the CLI accepts.
- [x] The three terminal-status sets.
- [x] `abandon_release` and the endpoint.
- [x] The delete, with all three refusals guarded individually — a delete whose refusals are only tested together is a delete with two untested refusals.

## Notes

**`superseded` was the alternative and it is the wrong word here.** [[ADR-0008]] made `superseded` a terminal phase status meaning *this was absorbed by that*. A release nobody shipped was not absorbed; it was dropped. `abandoned` says which of the two happened, and `superseded_by:` is available on it when the answer is *both*.
